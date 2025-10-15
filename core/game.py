from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

try:
    from core.dice import Dice
except Exception as e:
    class Dice:
        def __init__(self) -> None:
            self.__valores__ = []
            self.__restantes__ = []

        def tirar(self) -> None:
            raise RuntimeError("Dice no disponible. Implemente core/dice.py")

        def obtener_valores(self) -> List[int]:
            return list(self.__valores__)

        def movimientos_restantes(self) -> List[int]:
            return list(self.__restantes__)

        def consumir(self, v: int) -> None:
            raise RuntimeError("Dice no disponible.")

        def quedan_movimientos(self) -> bool:
            return bool(self.__restantes__)

        def reiniciar_turno(self) -> None:
            self.__valores__ = []
            self.__restantes__ = []

        def a_dict(self) -> Dict[str, Any]:
            return {"valores": self.__valores__, "restantes": self.__restantes__}

# Reusar constantes del Board para mantener consistencia de dominio.
try:
    from core.board import BLANCO, NEGRO, NUM_POINTS
except Exception:
    BLANCO = "blanco"  # fallback
    NEGRO = "negro"
    NUM_POINTS = 24

@runtime_checkable
class DicePort(Protocol):
    def tirar(self) -> None: ...
    def obtener_valores(self) -> List[int]: ...
    def movimientos_restantes(self) -> List[int]: ...
    def consumir(self, v: int) -> None: ...
    def quedan_movimientos(self) -> bool: ...
    def reiniciar_turno(self) -> None: ...
    def a_dict(self) -> Dict[str, Any]: ...

@runtime_checkable
class BoardPort(Protocol):
    def mover(self, jugador: str, origen: int, destino: int) -> bool: ...
    def puede_mover(self, jugador: str, valores: List[int]) -> bool: ...
    def pasos(self, jugador: str, origen: int, destino: int) -> int: ...

class BoardAdapter(BoardPort):
    """
    Adaptador a la API en español del Board:
    - es_movimiento_legal, aplicar_movimiento, calcular_destino_barra
    Colores esperados: 'blanco' | 'negro'.
    """
    def __init__(self, raw_board: Any) -> None:
        self._b = raw_board

    def mover(self, jugador: str, origen: int, destino: int) -> bool:
        # Usa la operación unificada del Board (maneja barra cuando origen == -1)
        try:
            # Validación básica: evita mutar si está bloqueado
            if hasattr(self._b, "es_movimiento_legal") and origen != -1:
                if not self._b.es_movimiento_legal(origen, destino, jugador):
                    return False
            if hasattr(self._b, "aplicar_movimiento"):
                return bool(self._b.aplicar_movimiento(origen, destino, jugador))
            # Fallback mínimo (no recomendado): movimiento directo sin validación adicional
            if origen == -1 and hasattr(self._b, "mover_desde_barra"):
                return bool(self._b.mover_desde_barra(jugador, destino))
            if hasattr(self._b, "mover_ficha"):
                self._b.mover_ficha(origen, destino)
                return True
        except Exception:
            return False
        return False

    def puede_mover(self, jugador: str, valores: List[int]) -> bool:
        try:
            if hasattr(self._b, "puede_mover"):
                return bool(self._b.puede_mover(jugador, list(valores)))
        except Exception:
            pass
        # Conservador: si no se puede consultar, asumimos que no
        return False

    def pasos(self, jugador: str, origen: int, destino: int) -> int:
        # Para el match con dados, los pasos son positivos.
        # - origen == -1 (barra): transformar destino a tirada válida.
        # - movimiento normal: diferencia absoluta.
        if origen == -1:
            if jugador == BLANCO:
                # reingreso 1..6 -> índices 0..5
                if 0 <= destino <= 5:
                    return destino + 1
            elif jugador == NEGRO:
                # reingreso 1..6 -> índices 23..18
                if 18 <= destino <= 23:
                    return 24 - destino
            raise ValueError("Destino inválido para reingreso desde barra.")
        diff = abs(int(destino) - int(origen))
        if diff <= 0:
            raise ValueError("Origen y destino deben ser distintos y producir pasos positivos.")
        return diff

class MovementRule(Protocol):
    def calcular_pasos(self, board: BoardPort, jugador: str, origen: int, destino: int) -> int: ...
    def seleccionar_dado(self, disponibles: List[int], pasos: int) -> int: ...

class BasicMovementRule:
    def calcular_pasos(self, board: BoardPort, jugador: str, origen: int, destino: int) -> int:
        return board.pasos(jugador, origen, destino)

    def seleccionar_dado(self, disponibles: List[int], pasos: int) -> int:
        if pasos in disponibles:
            return pasos
        raise ValueError(f"Movimiento de {pasos} no disponible. Restantes: {disponibles}")

class Game:
    """
    Orquesta turnos y dados con un Board inyectado (DIP).
    Abierto a nuevas reglas de movimiento vía MovementRule (OCP).
    """
    def __init__(
        self,
        board: Any,
        dice: Optional[DicePort] = None,
        jugador_inicial: str = BLANCO,
        movement_rule: Optional[MovementRule] = None,
        board_adapter_factory: Any = BoardAdapter,
    ) -> None:
        self.board: BoardPort = board if isinstance(board, BoardPort) else board_adapter_factory(board)
        self.dice: DicePort = dice if dice is not None else Dice()  # type: ignore[assignment]
        self.jugador_actual: str = jugador_inicial
        self.movement_rule: MovementRule = movement_rule if movement_rule is not None else BasicMovementRule()

    def comenzar_turno(self) -> bool:
        self.dice.reiniciar_turno()
        self.dice.tirar()
        if not self.puede_mover():
            self.pasar_turno_por_bloqueo()
            return False
        return True

    def terminar_turno(self) -> None:
        self.jugador_actual = NEGRO if self.jugador_actual == BLANCO else BLANCO
        self.dice.reiniciar_turno()

    def pasar_turno_por_bloqueo(self) -> None:
        self.terminar_turno()

    def movimientos_disponibles(self) -> List[int]:
        return list(self.dice.movimientos_restantes())

    def puede_mover(self) -> bool:
        valores: List[int] = self.dice.obtener_valores()
        if not valores:
            return False
        return bool(self.board.puede_mover(self.jugador_actual, valores))

    def realizar_movimiento(self, origen: int, destino: int) -> bool:
        """
        Movimiento simple con consumo de un dado.
        Valida y selecciona el dado vía MovementRule; delega la ejecución al BoardPort.
        """
        if not self.dice.quedan_movimientos():
            raise ValueError("No hay movimientos disponibles. Tire los dados primero.")
        pasos = self.movement_rule.calcular_pasos(self.board, self.jugador_actual, origen, destino)
        disponibles = self.movimientos_disponibles()
        dado_a_consumir = self.movement_rule.seleccionar_dado(disponibles, pasos)
        mover_ok = self.board.mover(self.jugador_actual, origen, destino)
        if not mover_ok:
            raise ValueError("Movimiento ilegal según el Board.")
        self.dice.consumir(dado_a_consumir)
        return True

    def a_dict(self) -> Dict[str, Any]:
        """Serializa el estado mínimo del juego."""
        return {
            "jugador_actual": self.jugador_actual,
            "dados": self.dice.a_dict(),
            "movimientos_disponibles": self.movimientos_disponibles(),
        }

  
