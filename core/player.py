"""Jugador y helpers de interacción con el tablero y los dados."""

from __future__ import annotations
import random
from typing import Iterable, List, Optional, TYPE_CHECKING

from .checker import Checker, BLANCO, NEGRO

if TYPE_CHECKING:
    from .board import Board  # solo para type hints, evita ciclos de import


class Player:
    """Jugador con utilidades para tirar dados y operar sobre un Board."""

    def __init__(self, color: str, nombre: Optional[str] = None) -> None:
        """Crear jugador validando el color y fijando un nombre opcional."""
        Checker.validate_color(color)
        self.__color__: str = color
        self.__nombre__: Optional[str] = nombre

    @property
    def color(self) -> str:
        """Color del jugador ('blanco' o 'negro')."""
        return self.__color__

    @property
    def nombre(self) -> Optional[str]:
        """Nombre descriptivo del jugador (si se proporcionó)."""
        return self.__nombre__

    # Dados
    def tirar_dados(self, rng: random.Random | None = None) -> List[int]:
        """Tira dos dados; retorna lista de valores (4 si fue doble)."""
        r = rng or random
        d1, d2 = r.randint(1, 6), r.randint(1, 6)
        if d1 == d2:
            return [d1, d1, d1, d1]
        return [d1, d2]

    # Alias en inglés
    def roll_dice(self, rng: random.Random | None = None) -> List[int]:
        """Alias en inglés de `tirar_dados`."""
        return self.tirar_dados(rng)

    # Consultas
    def puede_mover(self, board: "Board", tiradas: Iterable[int]) -> bool:
        """True si el board indica que puede mover con las tiradas dadas."""
        return board.puede_mover(self.color, list(tiradas))

    def can_move(self, board: "Board", dice: Iterable[int]) -> bool:
        """Alias en inglés de `puede_mover`."""
        return self.puede_mover(board, dice)

    def direccion(self, board: "Board") -> int:
        """Dirección de avance según el Board."""
        return board.direction(self.color)

    def direction(self, board: "Board") -> int:
        """Alias en inglés de `direccion`."""
        return self.direccion(board)

    # Acciones
    def mover(self, board: "Board", origen: int, paso: int) -> bool:
        """
        origen: índice 0..23 o -1 para barra
        paso: valor del dado
        """
        try:
            destino = (
                board.calcular_destino_barra(self.color, paso)
                if origen == -1
                else board.calcular_destino(origen, self.color, paso)
            )
        except Exception:  # pylint: disable=broad-exception-caught
            return False

        if not board.es_movimiento_legal(origen, destino, self.color):
            return False
        return bool(board.aplicar_movimiento(origen, destino, self.color))

    def move(self, board: "Board", origin: int, die: int) -> bool:
        """Alias en inglés de `mover`."""
        return self.mover(board, origin, die)

    def bornear(self, board: "Board", origen: int) -> bool:
        """Intenta bornear una ficha; retorna False si no fue posible."""
        try:
            board.bornear_ficha(origen, self.color)
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    def bear_off(self, board: "Board", origin: int) -> bool:
        """Alias en inglés de `bornear`."""
        return self.bornear(board, origin)

# Aliases y constantes útiles
__all__ = ["Player", "BLANCO", "NEGRO"]
