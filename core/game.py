"""Turn orchestration, dice consumption and board adapter for Backgammon."""
# pylint: disable=too-many-arguments,too-many-positional-arguments
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

try:
    from core.dice import Dice
except ImportError:
    class Dice:
        """Fallback Dice to avoid hard dependency during import failures."""

        def __init__(self) -> None:
            """Inicializa dados vacíos."""
            self.__valores__ = []
            self.__restantes__ = []

        def tirar(self) -> None:
            """No-op en fallback: indica que falta la implementación real."""
            raise RuntimeError("Dice no disponible. Implemente core/dice.py")

        def obtener_valores(self) -> List[int]:
            """Valores obtenidos (fallback)."""
            return list(self.__valores__)

        def movimientos_restantes(self) -> List[int]:
            """Movimientos restantes (fallback)."""
            return list(self.__restantes__)

        def consumir(self, v: int) -> None:
            """Consumo de valor (fallback)."""
            raise RuntimeError("Dice no disponible.")

        def quedan_movimientos(self) -> bool:
            """True si hay movimientos restantes."""
            return bool(self.__restantes__)

        def reiniciar_turno(self) -> None:
            """Reinicia el turno de dados."""
            self.__valores__ = []
            self.__restantes__ = []

        def a_dict(self) -> Dict[str, Any]:
            """Serialización mínima del estado del dado."""
            return {"valores": self.__valores__, "restantes": self.__restantes__}

# Reusar constantes del Board para mantener consistencia de dominio.
try:
    from core.board import BLANCO, NEGRO
except ImportError:
    BLANCO = "blanco"  # fallback
    NEGRO = "negro"


@runtime_checkable
class DicePort(Protocol):
    """Contrato de dados usado por Game."""
    def tirar(self) -> None:
        """Tira los dados (efecto lateral en el estado)."""
        ...
    def obtener_valores(self) -> List[int]:
        """Valores obtenidos para el turno actual (dobles => 4)."""
        ...
    def movimientos_restantes(self) -> List[int]:
        """Valores aún no consumidos en este turno."""
        ...
    def consumir(self, v: int) -> None:
        """Consume un valor 'v' de los movimientos restantes."""
        ...
    def quedan_movimientos(self) -> bool:
        """True si quedan valores por consumir."""
        ...
    def reiniciar_turno(self) -> None:
        """Reinicia el estado de los dados para un nuevo turno."""
        ...
    def a_dict(self) -> Dict[str, Any]:
        """Serializa el estado de los dados."""
        ...


@runtime_checkable
class BoardPort(Protocol):
    """Contrato del tablero usado por Game."""
    def mover(self, jugador: str, origen: int, destino: int) -> bool:
        """Aplica un movimiento en el tablero. Retorna True si se aplicó."""
        ...
    def puede_mover(self, jugador: str, valores: List[int]) -> bool:
        """True si existe alguna jugada válida con los valores provistos."""
        ...
    def pasos(self, jugador: str, origen: int, destino: int) -> int:
        """Cantidad de pasos positivos entre origen y destino (o desde barra)."""
        ...


class BoardAdapter(BoardPort):
    """
    Adaptador a la API en español del Board:
    - es_movimiento_legal, aplicar_movimiento, mover_desde_barra
    Colores esperados: 'blanco' | 'negro'.
    """

    def __init__(self, raw_board: Any) -> None:
        self._b = raw_board

    def mover(self, jugador: str, origen: int, destino: int) -> bool:
        """Aplica un movimiento usando la API disponible del Board."""
        try:
            if hasattr(self._b, "es_movimiento_legal") and origen != -1:
                if not self._b.es_movimiento_legal(origen, destino, jugador):
                    return False
            if hasattr(self._b, "aplicar_movimiento"):
                return bool(self._b.aplicar_movimiento(origen, destino, jugador))
            if origen == -1 and hasattr(self._b, "mover_desde_barra"):
                return bool(self._b.mover_desde_barra(jugador, destino))
            if hasattr(self._b, "mover_ficha"):
                self._b.mover_ficha(origen, destino)
                return True
        except (RuntimeError, ValueError, AttributeError, TypeError):
            return False
        return False

    def puede_mover(self, jugador: str, valores: List[int]) -> bool:
        """True si el board indica que se puede mover con los valores dados."""
        try:
            if hasattr(self._b, "puede_mover"):
                return bool(self._b.puede_mover(jugador, list(valores)))
        except (RuntimeError, ValueError, AttributeError, TypeError):
            # Ignorar errores del board y caer al fallback
            pass
        # Fallback: si el board no expone API, permitir si hay algún dado.
        # La legalidad concreta se verifica en mover().
        return bool(valores)

    def pasos(self, jugador: str, origen: int, destino: int) -> int:
        """
        Calcula pasos positivos para matchear contra los dados.
        Maneja:
          - origen == -1 (barra): mapear destino a tirada válida.
          - movimiento normal: diferencia absoluta.
        """
        if origen == -1:
            if jugador == BLANCO:
                if 0 <= destino <= 5:
                    return destino + 1
            elif jugador == NEGRO:
                if 18 <= destino <= 23:
                    return 24 - destino
            raise ValueError("Destino inválido para reingreso desde barra.")
        diff = abs(int(destino) - int(origen))
        if diff <= 0:
            raise ValueError("Origen y destino deben ser distintos con pasos positivos.")
        return diff


class MovementRule(Protocol):
    """Estrategia para calcular pasos y elegir el dado a consumir."""
    def calcular_pasos(self, board: BoardPort, jugador: str, origen: int, destino: int) -> int: ...
    def seleccionar_dado(self, disponibles: List[int], pasos: int) -> int: ...


class BasicMovementRule:
    """Regla por defecto: pasos desde board y consumir el dado igual a pasos."""

    def calcular_pasos(self, board: BoardPort, jugador: str, origen: int, destino: int) -> int:
        """Delegar el cálculo de pasos al BoardPort."""
        return board.pasos(jugador, origen, destino)

    def seleccionar_dado(self, disponibles: List[int], pasos: int) -> int:
        """Selecciona el dado igual a 'pasos' si está disponible."""
        if pasos in disponibles:
            return pasos
        # dividir mensaje largo para evitar C0301
        msg = f"Movimiento de {pasos} no disponible. Restantes: {disponibles}"
        raise ValueError(msg)


class Game:
    """Orquesta turnos y dados con un Board inyectado (DIP)."""

    def __init__(
        self,
        board: Any,
        dice: Optional[DicePort] = None,
        jugador_inicial: str = BLANCO,
        movement_rule: Optional[MovementRule] = None,
        board_adapter_factory: Any = BoardAdapter,
    ) -> None:  # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Inicializa el juego con tablero, dados y regla de movimiento."""
        self.board: BoardPort = board if isinstance(board, BoardPort) else board_adapter_factory(board)
        self.dice: DicePort = dice if dice is not None else Dice()  # type: ignore[assignment]
        self.jugador_actual: str = jugador_inicial
        self.movement_rule: MovementRule = movement_rule if movement_rule is not None else BasicMovementRule()

    def comenzar_turno(self) -> bool:
        """Tira dados y retorna True si hay jugadas; si no, pasa el turno."""
        self.dice.reiniciar_turno()
        self.dice.tirar()
        if not self.puede_mover():
            self.pasar_turno_por_bloqueo()
            return False
        return True

    def terminar_turno(self) -> None:
        """Alterna jugador y reinicia el estado de dados."""
        self.jugador_actual = NEGRO if self.jugador_actual == BLANCO else BLANCO
        self.dice.reiniciar_turno()

    def pasar_turno_por_bloqueo(self) -> None:
        """Pasa turno cuando no hay movimientos posibles."""
        self.terminar_turno()

    def movimientos_disponibles(self) -> List[int]:
        """Lista de movimientos restantes a consumir (dados)."""
        return list(self.dice.movimientos_restantes())

    def puede_mover(self) -> bool:
        """True si hay valores de dados y el board permite mover."""
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


