"""Checker value-object and color helpers for Backgammon domain."""
from dataclasses import FrozenInstanceError

BLANCO = "blanco"
NEGRO = "negro"
COLORES_VALIDOS = {BLANCO, NEGRO}


class Checker:
    """Representa una ficha con su color ('blanco' o 'negro')."""

    __slots__ = ("__color__",)

    def __init__(self, color: str) -> None:
        self.validate_color(color)
        object.__setattr__(self, "__color__", color)

    @property
    def color(self) -> str:
        """Color actual de la ficha."""
        return self.__color__

    def __setattr__(self, name: str, value) -> None:
        """Impide reasignar atributos para mantener inmutabilidad."""
        raise FrozenInstanceError(f"Checker es inmutable; no se puede modificar '{name}'.")

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
