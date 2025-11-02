"""
Detección de puntas (hit test) para el tablero.
"""

from typing import Tuple, List, Optional

Punto = Tuple[float, float]
Triangulo = Tuple[Punto, Punto, Punto]


class DeteccionPuntas:
    """
    Provee utilidades para detectar en qué punta cae un punto de la pantalla.

    Atributos:
        self.__triangulos__ (List[Triangulo]): Lista de triángulos (24 puntas).
    """

    def __init__(self, triangulos: List[Triangulo]) -> None:
        """
        Inicializa con la lista de triángulos.

        Parámetros:
            triangulos (List[Triangulo]): Puntas del tablero.
        """
        self.__triangulos__ = triangulos

    def actualizar_triangulos(self, triangulos: List[Triangulo]) -> None:
        """
        Actualiza la lista de triángulos (por ejemplo, tras un resize).

        Parámetros:
            triangulos (List[Triangulo]): Nueva lista de puntas.
        """
        self.__triangulos__ = triangulos

    def punto_en_triangulo(self, p: Punto, t: Triangulo) -> bool:
        """
        Indica si un punto p está dentro del triángulo t.

        Parámetros:
            p (Punto): Coordenadas (x, y).
            t (Triangulo): Vértices ((x1,y1),(x2,y2),(x3,y3)).

        Retorna:
            bool: True si p está dentro, False si no.
        """
        (x, y) = p
        (x1, y1), (x2, y2), (x3, y3) = t

        def signo(px, py, qx, qy, rx, ry):
            return (px - rx) * (qy - ry) - (qx - rx) * (py - ry)

        b1 = signo(x, y, x1, y1, x2, y2) < 0.0
        b2 = signo(x, y, x2, y2, x3, y3) < 0.0
        b3 = signo(x, y, x3, y3, x1, y1) < 0.0
        return (b1 == b2) and (b2 == b3)

    def buscar_indice_punta(self, pos: Punto) -> Optional[int]:
        """
        Devuelve el índice de la punta que contiene el punto pos.

        Parámetros:
            pos (Punto): Coordenadas (x, y).

        Retorna:
            Optional[int]: Índice [0..23] o None si no hay intersección.
        """
        for i, tri in enumerate(self.__triangulos__):
            if self.punto_en_triangulo(pos, tri):
                return i
        return None