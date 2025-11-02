"""
Tema visual del tablero (colores).
"""

from dataclasses import dataclass
from typing import Tuple, Dict

Color = Tuple[int, int, int]


@dataclass(frozen=True)
class TemaTablero:
    """
    Provee colores del tablero y fichas.

    Atributos (todas dunder):
      __madera__, __madera_oscura__, __punta_a__, __punta_b__, __barra__, __marco__,
      __resalte__, __texto__, __fondo__, __ficha_clara__, __ficha_oscura__, __borde_ficha__.
    """

    __madera__: Color = (186, 140, 99)
    __madera_oscura__: Color = (139, 94, 60)
    __punta_a__: Color = (234, 225, 210)
    __punta_b__: Color = (86, 60, 50)
    __barra__: Color = (70, 50, 40)
    __marco__: Color = (50, 35, 25)
    __resalte__: Color = (255, 210, 0)
    __texto__: Color = (25, 25, 25)
    __fondo__: Color = (20, 20, 20)
    __ficha_clara__: Color = (240, 240, 240)
    __ficha_oscura__: Color = (30, 30, 30)
    __borde_ficha__: Color = (10, 10, 10)

    def color_punta(self, indice_columna: int) -> Color:
        """
        Devuelve el color alternado de punta.
        - Param: indice_columna (int).
        - Return: Color.
        """
        return self.__punta_a__ if (indice_columna % 2 == 0) else self.__punta_b__

    def mapa_colores(self) -> Dict[str, Color]:
        """
        Devuelve un dict nombre→Color con todos los colores.
        """
        return {
            "__madera__": self.__madera__,
            "__madera_oscura__": self.__madera_oscura__,
            "__punta_a__": self.__punta_a__,
            "__punta_b__": self.__punta_b__,
            "__barra__": self.__barra__,
            "__marco__": self.__marco__,
            "__resalte__": self.__resalte__,
            "__texto__": self.__texto__,
            "__fondo__": self.__fondo__,
            "__ficha_clara__": self.__ficha_clara__,
            "__ficha_oscura__": self.__ficha_oscura__,
            "__borde_ficha__": self.__borde_ficha__,
        }

    def validar_colores(self) -> None:
        """
        Valida formato y rango RGB de todos los colores.
        - Raise: ValueError si hay valores inválidos.
        """
        for nombre, color in self.mapa_colores().items():
            if not (isinstance(color, tuple) and len(color) == 3):
                raise ValueError(f"Color inválido en {nombre}: {color!r}")
            r, g, b = color
            if any(not isinstance(c, int) or c < 0 or c > 255 for c in (r, g, b)):
                raise ValueError(f"Componente fuera de rango en {nombre}: {color!r}")