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