from dataclasses import dataclass

BLANCO = "blanco"
NEGRO = "negro"
COLORES_VALIDOS = {BLANCO, NEGRO}

@dataclass(frozen=True)
class Checker:
    color: str

    def __post_init__(self):
        if self.color not in COLORES_VALIDOS:
            raise ValueError(f"Color inválido: {self.color}. Debe ser 'blanco' o 'negro'.")

    @staticmethod
    def validate_color(color: str) -> None:
        if color not in COLORES_VALIDOS:
            raise ValueError(f"Color inválido: {color}. Debe ser 'blanco' o 'negro'.")

    def es_blanco(self) -> bool:
        return self.color == BLANCO

    def es_negro(self) -> bool:
        return self.color == NEGRO

    def contrario(self) -> str:
        return NEGRO if self.color == BLANCO else BLANCO

# Aliases exportables
__all__ = ["Checker", "BLANCO", "NEGRO", "COLORES_VALIDOS"]
