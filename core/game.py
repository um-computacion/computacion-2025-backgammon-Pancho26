from typing import Any, Dict, List, Optional
from typing import Protocol, runtime_checkable

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

WHITE = "white"
BLACK = "black"

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
    def __init__(self, raw_board: Any) -> None:
        self._b = raw_board

    def mover(self, jugador: str, origen: int, destino: int) -> bool:
        if hasattr(self._b, "mover"):
            return bool(self._b.mover(jugador, origen, destino))
        if hasattr(self._b, "mover_ficha"):
            return bool(self._b.mover_ficha(jugador, origen, destino))
        raise AttributeError("El Board no expone métodos de movimiento compatibles (mover/mover_ficha).")

    def puede_mover(self, jugador: str, valores: List[int]) -> bool:
        if hasattr(self._b, "puede_mover"):
            try:
                return bool(self._b.puede_mover(jugador, valores))
            except TypeError:
                return bool(self._b.puede_mover(jugador))
            except Exception:
                return bool(valores)
        return bool(valores)

    def pasos(self, jugador: str, origen: int, destino: int) -> int:
        if hasattr(self._b, "pasos"):
            try:
                return int(self._b.pasos(jugador, origen, destino))
            except Exception:
                pass
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
    """Orquesta turnos y dados con un Board inyectado."""

    def __init__(
        self,
        board: Any,
        dice: Optional[DicePort] = None,
        jugador_inicial: str = WHITE,
        movement_rule: Optional[MovementRule] = None,
        board_adapter_factory: Any = BoardAdapter,
    ) -> None:
        self.board: BoardPort = board if isinstance(board, BoardPort) else board_adapter_factory(board)
        self.dice: DicePort = dice if dice is not None else Dice()  # type: ignore[assignment]
        self.jugador_actual: str = jugador_inicial
        self.movement_rule: MovementRule = movement_rule if movement_rule is not None else BasicMovementRule()

    def comenzar_turno(self) -> bool:
        try:
            self.dice.reiniciar_turno()
        except Exception:
            pass
        self.dice.tirar()
        if not self.puede_mover():
            self.pasar_turno_por_bloqueo()
            return False
        return True

    def terminar_turno(self) -> None:
        self.jugador_actual = BLACK if self.jugador_actual == WHITE else WHITE
        self.dice.reiniciar_turno()

    def pasar_turno_por_bloqueo(self) -> None:
        self.terminar_turno()

    def movimientos_disponibles(self) -> List[int]:
        try:
            return list(self.dice.movimientos_restantes())
        except Exception:
            return []

    def puede_mover(self) -> bool:
        valores: List[int] = []
        try:
            valores = self.dice.obtener_valores()
        except Exception:
            pass
        if not valores:
            return False
        try:
            return bool(self.board.puede_mover(self.jugador_actual, valores))
        except Exception:
            return True

    def realizar_movimiento(self, origen: int, destino: int) -> bool:
        """Movimiento simple que consume un dado."""
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

    def _calcular_pasos(self, origen: int, destino: int) -> int:
        return self.board.pasos(self.jugador_actual, origen, destino)

    def a_dict(self) -> Dict[str, Any]:
        """Estado mínimo del juego."""
        return {
            "jugador_actual": self.jugador_actual,
            "dados": self.dice.a_dict() if hasattr(self.dice, "a_dict") else {},
            "movimientos_disponibles": self.movimientos_disponibles(),
        }
        try:
            valores = self.dice.obtener_valores()
        except Exception:
            pass

        if not valores:
            return False

        try:
            return bool(self.board.puede_mover(self.jugador_actual, valores))
        except Exception:
            return True

    # Movimiento

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

    # Utilidades

    def _calcular_pasos(self, origen: int, destino: int) -> int:
        """
        Compat: método legado. Se mantiene pero se delega a BoardPort.
        """
        return self.board.pasos(self.jugador_actual, origen, destino)

    def a_dict(self) -> Dict[str, Any]:
        """Serializa el estado mínimo del juego."""
        return {
            "jugador_actual": self.jugador_actual,
            "dados": self.dice.a_dict() if hasattr(self.dice, "a_dict") else {},
            "movimientos_disponibles": self.movimientos_disponibles(),
        }

    # TODO:
    # - Reglas avanzadas (reingreso desde la barra, borne, combinaciones, forzados).
    # - Detección de fin de partida.
