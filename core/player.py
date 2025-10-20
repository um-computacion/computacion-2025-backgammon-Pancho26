from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Iterable, List, Optional, TYPE_CHECKING

from .checker import Checker, BLANCO, NEGRO

if TYPE_CHECKING:
    from .board import Board  # solo para type hints, evita ciclos de import

@dataclass
class Player:
    color: str
    nombre: Optional[str] = None

    def __post_init__(self):
        Checker.validate_color(self.color)

    # Dados
    def tirar_dados(self, rng: random.Random | None = None) -> List[int]:
        r = rng or random
        d1, d2 = r.randint(1, 6), r.randint(1, 6)
        if d1 == d2:
            return [d1, d1, d1, d1]
        return [d1, d2]

    # Alias en inglés
    def roll_dice(self, rng: random.Random | None = None) -> List[int]:
        return self.tirar_dados(rng)

    # Consultas
    def puede_mover(self, board: "Board", tiradas: Iterable[int]) -> bool:
        return board.puede_mover(self.color, list(tiradas))

    def can_move(self, board: "Board", dice: Iterable[int]) -> bool:
        return self.puede_mover(board, dice)

    def direccion(self, board: "Board") -> int:
        return board.direction(self.color)

    def direction(self, board: "Board") -> int:
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
        except Exception:
            return False

        if not board.es_movimiento_legal(origen, destino, self.color):
            return False
        return bool(board.aplicar_movimiento(origen, destino, self.color))

    def move(self, board: "Board", origin: int, die: int) -> bool:
        return self.mover(board, origin, die)

    def bornear(self, board: "Board", origen: int) -> bool:
        try:
            board.bornear_ficha(origen, self.color)
            return True
        except Exception:
            return False

    def bear_off(self, board: "Board", origin: int) -> bool:
        return self.bornear(board, origin)

# Aliases y constantes útiles
__all__ = ["Player", "BLANCO", "NEGRO"]