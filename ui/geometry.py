"""
Geometría del tablero (rectángulos, triángulos, etiquetas).
"""

from dataclasses import dataclass
from typing import List, Tuple
import pygame

Color = Tuple[int, int, int]
Punto = Tuple[float, float]
Triangulo = Tuple[Punto, Punto, Punto]


@dataclass
class GeometriaTablero:
    """
    Contenedor inmutable de la geometría calculada del tablero.

    Atributos:
        __rect_tablero__ (pygame.Rect): Área del tablero.
        __rect_barra__ (pygame.Rect): Área de la barra central.
        __triangulos__ (List[Triangulo]): Triángulos de puntas (0..23).
        __etiquetas__ (List[int]): Numeración estándar BG por punta.
        __colores_puntas__ (List[Color]): Color alternado por punta.
        __altura_triangulo__ (float): Altura de cada triángulo.
        __ancho_punta__ (float): Ancho de cada punta.
    """
    __rect_tablero__: pygame.Rect
    __rect_barra__: pygame.Rect
    __triangulos__: List[Triangulo]
    __etiquetas__: List[int]
    __colores_puntas__: List[Color]
    __altura_triangulo__: float
    __ancho_punta__: float


class MotorDisposicion:
    """
    Calcula la disposición del tablero a partir del tamaño de ventana.

    Atributos:
        __margen__ (int): Margen interno del tablero.
        __fraccion_barra__ (float): Fracción del ancho para la barra.
    """

    def __init__(self, margen: int = 20, fraccion_barra: float = 0.06) -> None:
        """
        Inicializa el motor.

        Parámetros:
            margen (int): Margen interno.
            fraccion_barra (float): Ancho relativo de la barra central.
        """
        self.__margen__ = margen
        self.__fraccion_barra__ = fraccion_barra

    def construir(
        self,
        ancho: int,
        alto: int,
        color_punta_a: Color,
        color_punta_b: Color,
        color_barra: Color,  # no se usa aquí, lo dibuja el render
        offset_superior: int = 0,
    ) -> GeometriaTablero:
        """
        Construye la geometría del tablero.

        Parámetros:
            ancho (int): Ancho de ventana.
            alto (int): Alto de ventana.
            color_punta_a (Color): Color alternado A.
            color_punta_b (Color): Color alternado B.
            color_barra (Color): Color de barra (referencia).

        Retorna:
            GeometriaTablero: Datos geométricos listos para renderizar.
        """
        offset_superior = max(0, offset_superior)
        ancho_tablero = max(200, ancho - 2 * self.__margen__)
        alto_disponible = max(200, alto - offset_superior - 2 * self.__margen__)
        top = self.__margen__ + offset_superior
        rect_tablero = pygame.Rect(self.__margen__, top, ancho_tablero, alto_disponible)

        ancho_barra = max(48, int(ancho_tablero * self.__fraccion_barra__))
        ancho_punta = (ancho_tablero - ancho_barra) / 12.0
        altura_triangulo = max(16.0, (alto_disponible / 2.0) - 24)

        barra_x = self.__margen__ + int(ancho_punta * 6)
        rect_barra = pygame.Rect(barra_x, top, ancho_barra, alto_disponible)

        triangulos: List[Triangulo] = []
        colores_puntas: List[Color] = []
        etiquetas: List[int] = [0] * 24

        # Etiquetas: fila superior 13..24 (izq->der), fila inferior 12..1 (izq->der)
        for i in range(12):
            etiquetas[i] = 13 + i
        for i in range(12):
            etiquetas[12 + i] = 12 - i

        # Triángulos superiores
        for col in range(12):
            x0 = self.__margen__ + col * ancho_punta + (ancho_barra if col >= 6 else 0)
            base_y = top
            apice_y = top + altura_triangulo
            triangulos.append(((x0, base_y), (x0 + ancho_punta, base_y), (x0 + ancho_punta / 2.0, apice_y)))
            colores_puntas.append(color_punta_a if (col % 2 == 0) else color_punta_b)

        # Triángulos inferiores
        for col in range(12):
            x0 = self.__margen__ + col * ancho_punta + (ancho_barra if col >= 6 else 0)
            base_y = top + alto_disponible
            apice_y = top + alto_disponible - altura_triangulo
            triangulos.append(((x0, base_y), (x0 + ancho_punta, base_y), (x0 + ancho_punta / 2.0, apice_y)))
            colores_puntas.append(color_punta_a if (col % 2 == 0) else color_punta_b)

        return GeometriaTablero(
            __rect_tablero__=rect_tablero,
            __rect_barra__=rect_barra,
            __triangulos__=triangulos,
            __etiquetas__=etiquetas,
            __colores_puntas__=colores_puntas,
            __altura_triangulo__=altura_triangulo,
            __ancho_punta__=ancho_punta,
        )


__all__ = ["GeometriaTablero", "MotorDisposicion"]
