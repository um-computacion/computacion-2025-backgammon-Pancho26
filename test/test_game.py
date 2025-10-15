import unittest
from typing import Any, Dict, List

from core.game import Game, BLANCO, NEGRO, BoardPort, DicePort


class FakeDice(DicePort):
    """
    Dado determinista para tests.
    - valores_base: lista fija de dados del turno (p. ej., [3,5] o [6,6,6,6] para dobles)
    - tirar() no cambia los valores; sólo marca el turno activo si quisieras extenderlo.
    """
    def __init__(self, valores_base: List[int]) -> None:
        self._valores_base = list(valores_base)
        self._restantes: List[int] = []

    def tirar(self) -> None:
        # En este fake, tirar no altera la semilla ni randomiza; sólo confirma el estado.
        pass

    def obtener_valores(self) -> List[int]:
        return list(self._valores_base)

    def movimientos_restantes(self) -> List[int]:
        return list(self._restantes)

    def consumir(self, v: int) -> None:
        try:
            self._restantes.remove(v)
        except ValueError as e:
            raise ValueError("Valor no disponible") from e

    def quedan_movimientos(self) -> bool:
        return bool(self._restantes)

    def reiniciar_turno(self) -> None:
        # Al comenzar turno, se restablecen los movimientos restantes
        self._restantes = list(self._valores_base)

    def a_dict(self) -> Dict[str, Any]:
        return {"valores": list(self._valores_base), "restantes": list(self._restantes)}
class FakeBoard(BoardPort):
    """
    Tablero mínimo compatible con BoardPort.
    - puede_mover: se controla por bandera para simular bloqueo.
    - mover: configurable para aceptar o rechazar; registra la última llamada.
    - pasos: lógica simple + soporte de barra (-1) como en el adaptador real.
    """
    def __init__(self, puede_mover_flag: bool = True, mover_ok: bool = True) -> None:
        self.puede_mover_flag = puede_mover_flag
        self.mover_ok = mover_ok
        self.last_move = None  # (jugador, origen, destino)
        self.move_calls = 0

    def mover(self, jugador: str, origen: int, destino: int) -> bool:
        self.move_calls += 1
        self.last_move = (jugador, origen, destino)
        return bool(self.mover_ok)

    def puede_mover(self, jugador: str, valores: List[int]) -> bool:
        # Si no hay valores, no puede mover. Si hay, respeta la bandera.
        return bool(valores) and bool(self.puede_mover_flag)

    def pasos(self, jugador: str, origen: int, destino: int) -> int:
        if origen == -1:
            if jugador == BLANCO:
                if 0 <= destino <= 5:
                    return destino + 1
            else:  # NEGRO
                if 18 <= destino <= 23:
                    return 24 - destino
            raise ValueError("Destino inválido para reingreso desde barra.")
        diff = abs(int(destino) - int(origen))
        if diff <= 0:
            raise ValueError("Pasos inválidos (origen=destino).")
        return diff