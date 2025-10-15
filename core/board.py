from __future__ import annotations
from typing import List, Dict, Optional

BLANCO = "blanco"
NEGRO = "negro"

NUM_POINTS = 24
HOME_RANGE = {
    BLANCO: range(18, 24),
    NEGRO:  range(0, 6),    
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
        # Exponer alias esperados por los tests
        self.__posiciones__ = self._points
        self.__barra__ = self._bar
        self.__fichas_fuera__ = self._borne_off
        self.reset_to_start()

    def reset_to_start(self) -> None:
        """Coloca las fichas en posiciones estándar de inicio."""
        # Reemplazar contenido en lugar de re-binder para mantener alias válidos
        self._points[:] = [[] for _ in range(NUM_POINTS)]
        self._bar.clear(); self._bar[BLANCO] = []; self._bar[NEGRO] = []
        self._borne_off.clear(); self._borne_off[BLANCO] = []; self._borne_off[NEGRO] = []

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

    # --- Compatibilidad API en español (utilizado por tests) ---
    def inicializar_posiciones(self) -> None:
        """Alias de reset_to_start()."""
        self.reset_to_start()

    def obtener_punto(self, indice: int) -> List[str]:
        """Copia de la pila en el punto indicado."""
        return self.stack_at(indice)

    def obtener_barra(self, color: Optional[str] = None):
        """Copia de la barra (global o por color)."""
        return self.bar(color)

    def obtener_fuera(self, color: Optional[str] = None):
        """Copia de fichas borneadas (global o por color)."""
        return self.borne_off(color)

    def agregar_ficha(self, punto: int, color: str) -> None:
        """Alias de add_to_point()."""
        self.add_to_point(punto, color)

    def quitar_ficha(self, punto: int) -> Optional[str]:
        """Alias de remove_from_point()."""
        return self.remove_from_point(punto)

    def mover_ficha(self, origen: int, destino: int) -> None:
        """Mueve una ficha aplicando captura simple si hay una rival en destino."""
        ficha = self.remove_from_point(origen)
        if ficha is None:
            return
        destino_fichas = self._points[destino]
        if destino_fichas and len(destino_fichas) == 1 and destino_fichas[0] != ficha:
            capturado = self._points[destino].pop()
            self.push_to_bar(capturado)
        self._points[destino].append(ficha)

    def mover_desde_barra(self, color: str, destino: int) -> bool:
        """
        Mueve una ficha desde la barra al destino si no está bloqueado.
        Captura si hay una sola ficha rival.
        """
        self._require_color(color)
        if not self._bar[color]:
            return False
        destino_fichas = self._points[destino]
        # Bloqueado si hay 2+ del rival
        if destino_fichas and destino_fichas[0] != color and len(destino_fichas) > 1:
            return False

        # Sale de la barra
        self._bar[color].pop()

        # Captura si corresponde
        if destino_fichas and len(destino_fichas) == 1 and destino_fichas[0] != color:
            capturado = self._points[destino].pop()
            self.push_to_bar(capturado)

        self._points[destino].append(color)
        return True

    def aplicar_movimiento(self, origen: int, destino: int, color: str) -> bool:
        """Aplica un movimiento desde tablero o barra (origen == -1)."""
        if origen == -1:
            return self.mover_desde_barra(color, destino)
        self.mover_ficha(origen, destino)
        return True

    def contar_en_barra(self, color: str) -> int:
        """Cantidad de fichas en barra para el color."""
        return self.bar_count(color)

    def ha_ganado(self, color: str) -> bool:
        """True si el jugador borneó sus 15 fichas."""
        return self.borne_off_count(color) >= 15

    def obtener_estado_puntos(self) -> List[dict]:
        """Resumen de puntos: lista de dicts {color, cantidad}."""
        return self.points_snapshot()

    def bornear_ficha(self, punto: int, color: str) -> None:
        """Borneo directo sin validar reglas."""
        ficha = self.remove_from_point(punto)
        if ficha == color:
            self.push_borne_off(color)
        elif ficha is not None:
            # Revertir si no coincide el color
            self.add_to_point(punto, ficha)

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
        # Mantener alias esperados por tests en el clon
        nb.__posiciones__ = nb._points
        nb.__barra__ = nb._bar
        nb.__fichas_fuera__ = nb._borne_off
        return nb

  
    def _require_point(self, index: int) -> None:
        if not (0 <= index < NUM_POINTS):
            raise IndexError(f"Punto fuera de rango: {index}")

    def _require_color(self, color: str) -> None:
        if color not in (BLANCO, NEGRO):
            raise ValueError(f"Color inválido: {color}")

    def es_movimiento_legal(self, origen: int, destino: int, color: str) -> bool:
        """
        Movimiento legal si el destino no está bloqueado (2+ fichas rivales).
        - origen == -1: mover desde barra, requiere tener al menos una en barra.
        - origen 0..23: requiere ficha propia en el punto.
        (No valida distancias/ dados, sólo bloqueo básico.)
        """
        self._require_color(color)
        if not (0 <= destino < NUM_POINTS):
            return False

        def bloqueado(idx: int) -> bool:
            pila = self._points[idx]
            return bool(pila) and pila[0] != color and len(pila) > 1

        if origen == -1:
            # Desde barra: debe haber fichas en barra y destino no bloqueado
            if not self._bar[color]:
                return False
            return not bloqueado(destino)

        # Origen en tablero
        if not (0 <= origen < NUM_POINTS):
            return False
        pila_origen = self._points[origen]
        if not pila_origen or pila_origen[0] != color:
            return False

        return not bloqueado(destino)

    def calcular_destino(self, origen: int, color: str, tirada: int) -> int:
        """Calcula el destino desde un origen según color y tirada (no valida bloqueo)."""
        self._require_color(color)
        self._require_point(origen)
        return origen + DIRECTION[color] * tirada

    def calcular_destino_barra(self, color: str, tirada: int) -> int:
        """Calcula el punto de reingreso desde la barra según color y tirada."""
        self._require_color(color)
        # Blancas reingresan en 0..5 (tirada 1..6 => 0..5)
        if color == BLANCO:
            return tirada - 1
        # Negras reingresan en 23..18 (tirada 1..6 => 23..18)
        return 24 - tirada

    def puede_mover(self, color: str, tiradas: List[int]) -> bool:
        """True si existe algún movimiento legal con las tiradas dadas."""
        self._require_color(color)
        # Si hay fichas en barra, sólo se consideran reingresos
        if self._bar[color]:
            for d in tiradas:
                dest = self.calcular_destino_barra(color, d)
                if 0 <= dest < NUM_POINTS and self.es_movimiento_legal(-1, dest, color):
                    return True
            return False

        # Sin fichas en barra: buscar cualquier origen válido que pueda mover
        for origen in range(NUM_POINTS):
            pila = self._points[origen]
            if not pila or pila[0] != color:
                continue
            for d in tiradas:
                dest = self.calcular_destino(origen, color, d)
                if 0 <= dest < NUM_POINTS and self.es_movimiento_legal(origen, dest, color):
                    return True
        return False