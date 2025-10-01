from __future__ import annotations
from typing import List, Dict, Optional

BLANCO = "blanco"
NEGRO = "negro"

NUM_POINTS = 24
HOME_RANGE = {
    BLANCO: range(18, 24),  # 18..23
    NEGRO:  range(0, 6),    # 0..5
}
DIRECTION = {
    BLANCO: +1,
    NEGRO:  -1,
}


class Board:
    
    def __init__(self) -> None:
        self._points: List[List[str]] = [[] for _ in range(NUM_POINTS)]
        self._bar: Dict[str, List[str]] = {BLANCO: [], NEGRO: []}
        self._borne_off: Dict[str, List[str]] = {BLANCO: [], NEGRO: []}
        self.reset_to_start()

   
    def reset_to_start(self) -> None:
        """Coloca las fichas en posiciones estándar de inicio."""
        self._points = [[] for _ in range(NUM_POINTS)]
        self._bar = {BLANCO: [], NEGRO: []}
        self._borne_off = {BLANCO: [], NEGRO: []}

        self._points[0]  = [BLANCO] * 2
        self._points[11] = [BLANCO] * 5
        self._points[16] = [BLANCO] * 3
        self._points[18] = [BLANCO] * 5
        # Negras
        self._points[23] = [NEGRO] * 2
        self._points[12] = [NEGRO] * 5
        self._points[7]  = [NEGRO] * 3
        self._points[5]  = [NEGRO] * 5

   
    def stack_at(self, index: int) -> List[str]:
        """Copia de la pila en el punto `index` (0..23)."""
        self._require_point(index)
        return list(self._points[index])

    def bar(self, color: Optional[str] = None) -> Dict[str, List[str]] | List[str]:
        """Copia de la(s) barra(s)."""
        if color is None:
            return {c: list(p) for c, p in self._bar.items()}
        self._require_color(color)
        return list(self._bar[color])

    def borne_off(self, color: Optional[str] = None) -> Dict[str, List[str]] | List[str]:
        """Copia de las fichas borneadas."""
        if color is None:
            return {c: list(p) for c, p in self._borne_off.items()}
        self._require_color(color)
        return list(self._borne_off[color])

    def bar_count(self, color: str) -> int:
        self._require_color(color)
        return len(self._bar[color])

    def borne_off_count(self, color: str) -> int:
        self._require_color(color)
        return len(self._borne_off[color])

    def point_count(self, index: int) -> int:
        self._require_point(index)
        return len(self._points[index])

    def top_color_at(self, index: int) -> Optional[str]:
        """Color del tope en el punto, o None si vacío."""
        self._require_point(index)
        return self._points[index][-1] if self._points[index] else None

    def points_snapshot(self) -> List[dict]:
        """Resumen compacto de puntos (para UI/logs)."""
        out = []
        for pile in self._points:
            if pile:
                out.append({"color": pile[0], "cantidad": len(pile)})
            else:
                out.append({"color": None, "cantidad": 0})
        return out

    def is_home_point(self, color: str, index: int) -> bool:
        self._require_color(color)
        self._require_point(index)
        return index in HOME_RANGE[color]

    def direction(self, color: str) -> int:
        self._require_color(color)
        return DIRECTION[color]

 
    def add_to_point(self, index: int, color: str) -> None:
        """Agrega una ficha del `color` al punto `index`."""
        self._require_point(index)
        self._require_color(color)
        self._points[index].append(color)

    def remove_from_point(self, index: int) -> Optional[str]:
        """Saca y devuelve la ficha del tope del punto, o None si vacío."""
        self._require_point(index)
        if self._points[index]:
            return self._points[index].pop()
        return None

    def push_to_bar(self, color: str) -> None:
        """Envía una ficha del `color` a la barra (captura)."""
        self._require_color(color)
        self._bar[color].append(color)

    def pop_from_bar(self, color: str) -> Optional[str]:
        """Quita una ficha de la barra del `color`, o None si no hay."""
        self._require_color(color)
        if self._bar[color]:
            return self._bar[color].pop()
        return None

    def push_borne_off(self, color: str) -> None:
        """Agrega una ficha borneada (fuera) del `color`."""
        self._require_color(color)
        self._borne_off[color].append(color)

 
    def total_checkers(self, color: Optional[str] = None) -> int:
        """
        Cuenta fichas por color (o total si color=None) incluyendo puntos, barra y borneadas.
        Útil para tests de invariantes (debe ser 15 por color).
        """
        def count_color(c: str) -> int:
            points = sum(1 for pile in self._points for ch in pile if ch == c)
            bar = len(self._bar[c])
            off = len(self._borne_off[c])
            return points + bar + off

        if color is None:
            return count_color(BLANCO) + count_color(NEGRO)
        self._require_color(color)
        return count_color(color)

    def clone(self) -> "Board":
        """Copia profunda liviana (para simulaciones/tests)."""
        nb = Board.__new__(Board)  # evita reset_to_start
        nb._points = [list(p) for p in self._points]
        nb._bar = {c: list(p) for c, p in self._bar.items()}
        nb._borne_off = {c: list(p) for c, p in self._borne_off.items()}
        return nb

  
    def _require_point(self, index: int) -> None:
        if not (0 <= index < NUM_POINTS):
            raise IndexError(f"Punto fuera de rango: {index}")

    def _require_color(self, color: str) -> None:
        if color not in (BLANCO, NEGRO):
            raise ValueError(f"Color inválido: {color}")
        
"""
Tablero de Backgammon (SRP: sólo estado y operaciones atómicas).
La validación de reglas se delega a un objeto Rules (Strategy).
"""
from __future__ import annotations
from typing import List, Dict, Optional, Sequence, Any
from .rules import Rules, StandardBackgammonRules, BLANCO, NEGRO


class Board:
    """
    Representa el tablero con:
      - 24 puntos (pilas de colores)
      - barra por color
      - fichas borneadas por color
    """

    def __init__(self, rules: Optional[Rules] = None):
        """
        Args:
            rules: implementación de Rules a usar. Por defecto StandardBackgammonRules.
        """
        self.__posiciones__: List[List[str]] = [[] for _ in range(24)]
        self.__barra__: Dict[str, List[str]] = {BLANCO: [], NEGRO: []}
        self.__fichas_fuera__: Dict[str, List[str]] = {BLANCO: [], NEGRO: []}
        self.__rules__: Rules = rules or StandardBackgammonRules()
        self.inicializar_posiciones()

    def inicializar_posiciones(self) -> None:
        """Coloca las fichas en las posiciones estándar de inicio."""
        # Blancas
        self.__posiciones__[0] = [BLANCO] * 2
        self.__posiciones__[11] = [BLANCO] * 5
        self.__posiciones__[16] = [BLANCO] * 3
        self.__posiciones__[18] = [BLANCO] * 5
        # Negras
        self.__posiciones__[23] = [NEGRO] * 2
        self.__posiciones__[12] = [NEGRO] * 5
        self.__posiciones__[7] = [NEGRO] * 3
        self.__posiciones__[5] = [NEGRO] * 5

    def agregar_ficha(self, punto: int, color: str) -> None:
        """
        Agrega una ficha al punto.
        Args:
            punto: índice 0..23.
            color: 'blanco' o 'negro'.
        """
        self.__posiciones__[punto].append(color)

    def quitar_ficha(self, punto: int) -> Optional[str]:
        """
        Quita y devuelve la ficha superior del punto.
        Args:
            punto: índice 0..23.
        Returns:
            Color de la ficha o None si el punto está vacío.
        """
        if self.__posiciones__[punto]:
            return self.__posiciones__[punto].pop()
        return None

    def mover_ficha(self, origen: int, destino: int) -> None:
        """
        Mueve una ficha del origen al destino, aplicando captura si hay una sola rival.
        Args:
            origen: índice 0..23.
            destino: índice 0..23.
        """
        ficha = self.quitar_ficha(origen)
        if not ficha:
            return
        destino_fichas = self.__posiciones__[destino]
        if destino_fichas and len(destino_fichas) == 1 and destino_fichas[0] != ficha:
            capturado = self.__posiciones__[destino].pop()
            self.__barra__[capturado].append(capturado)
        self.agregar_ficha(destino, ficha)

    def es_movimiento_legal(self, origen: int, destino: int, color: str) -> bool:
        """
        Delegado a Rules.
        Args:
            origen: -1 (barra) o 0..23.
            destino: 0..23.
            color: 'blanco' o 'negro'.
        """
        return self.__rules__.es_movimiento_legal(self, origen, destino, color)

    def puede_mover(self, color: str, tiradas: Sequence[int]) -> bool:
        """
        True si existe algún movimiento legal con las tiradas.
        Args:
            color: 'blanco' o 'negro'.
            tiradas: lista de valores disponibles.
        """
        return self.__rules__.puede_mover(self, color, tiradas)

    def calcular_destino(self, origen: int, color: str, tirada: int) -> int:
        """Calcula destino desde un punto."""
        return self.__rules__.calcular_destino(origen, color, tirada)

    def calcular_destino_barra(self, color: str, tirada: int) -> int:
        """Calcula destino al reingresar desde la barra."""
        return self.__rules__.calcular_destino_barra(color, tirada)

    def bornear_ficha(self, punto: int, color: str) -> None:
        """
        Borneo directo (sin validar).
        Args:
            punto: índice 0..23.
            color: 'blanco' o 'negro'.
        """
        ficha = self.quitar_ficha(punto)
        if ficha == color:
            self.__fichas_fuera__[color].append(ficha)

    def todos_en_casa(self, color: str) -> bool:
        """Delegado a Rules: True si todas las fichas están en el tablero interno."""
        return self.__rules__.todos_en_casa(self, color)

    def puede_bornear(self, origen: int, color: str, tirada: int) -> bool:
        """Delegado a Rules: valida si se puede bornear con la tirada dada."""
        return self.__rules__.puede_bornear(self, origen, color, tirada)

    def bornear_si_valido(self, origen: int, color: str, tirada: int) -> bool:
        """
        Borneo si es legal según la tirada.
        Returns:
            True si se realizó el borneo.
        """
        if not self.puede_bornear(origen, color, tirada):
            return False
        ficha = self.quitar_ficha(origen)
        if ficha == color:
            self.__fichas_fuera__[color].append(ficha)
            return True
        if ficha is not None:
            self.agregar_ficha(origen, ficha)
        return False

    def contar_en_barra(self, color: str) -> int:
        """Cantidad de fichas en barra para el color."""
        return len(self.__barra__[color])

    def ha_ganado(self, color: str) -> bool:
        """True si el jugador borneó sus 15 fichas."""
        return len(self.__fichas_fuera__[color]) >= 15

    def obtener_estado_puntos(self) -> List[Dict[str, Any]]:
        """Resumen de puntos: lista de dicts {color, cantidad} para UI/logs."""
        estado: List[Dict[str, Any]] = []
        for pila in self.__posiciones__:
            if pila:
                estado.append({"color": pila[0], "cantidad": len(pila)})
            else:
                estado.append({"color": None, "cantidad": 0})
        return estado

    def obtener_punto(self, indice: int) -> List[str]:
        """Copia de la pila en el punto indicado."""
        return list(self.__posiciones__[indice])

    def obtener_barra(self, color: Optional[str] = None):
        """Copia de la barra (global o por color)."""
        if color is None:
            return {c: list(p) for c, p in self.__barra__.items()}
        return list(self.__barra__[color])

    def obtener_fuera(self, color: Optional[str] = None):
        """Copia de fichas borneadas (global o por color)."""
        if color is None:
            return {c: list(p) for c, p in self.__fichas_fuera__.items()}
        return list(self.__fichas_fuera__[color])

    def mover_desde_barra(self, color: str, destino: int) -> bool:
        """
        Mueve una ficha desde la barra al destino si es válido (maneja captura).
        Returns:
            True si movió.
        """
        if not self.__barra__[color]:
            return False
        destino_fichas = self.__posiciones__[destino]
        if destino_fichas and destino_fichas[0] != color and len(destino_fichas) > 1:
            return False

        self.__barra__[color].pop()

        if destino_fichas and len(destino_fichas) == 1 and destino_fichas[0] != color:
            capturado = self.__posiciones__[destino].pop()
            self.__barra__[capturado].append(capturado)

        self.__posiciones__[destino].append(color)
        return True

    def aplicar_movimiento(self, origen: int, destino: int, color: str) -> bool:
      
        if origen == -1:
            return self.mover_desde_barra(color, destino)
        self.mover_ficha(origen, destino)
        return True