"""Checker value-object and color helpers for Backgammon domain."""
from dataclasses import dataclass

BLANCO = "blanco"
NEGRO = "negro"
COLORES_VALIDOS = {BLANCO, NEGRO}


@dataclass(frozen=True)
class Checker:
    """Representa una ficha con su color ('blanco' o 'negro')."""

    color: str

    def __post_init__(self):
        """Valida el color al construir la ficha."""
        if self.color not in COLORES_VALIDOS:
            raise ValueError(f"Color inválido: {self.color}. Debe ser 'blanco' o 'negro'.")

    @staticmethod
    def validate_color(color: str) -> None:
        """Lanza ValueError si el color no es válido."""
        if color not in COLORES_VALIDOS:
            raise ValueError(f"Color inválido: {color}. Debe ser 'blanco' o 'negro'.")

    def es_blanco(self) -> bool:
        """True si la ficha es blanca."""
        return self.color == BLANCO

    def es_negro(self) -> bool:
        """True si la ficha es negra."""
        return self.color == NEGRO

    def contrario(self) -> str:
        """Devuelve el color contrario a self.color."""
        return NEGRO if self.color == BLANCO else BLANCO

# Aliases exportables
__all__ = ["Checker", "BLANCO", "NEGRO", "COLORES_VALIDOS"]
