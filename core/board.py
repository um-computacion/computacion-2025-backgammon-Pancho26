"""In-memory Backgammon board representation and basic rules/helpers."""
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
    """Tablero con puntos, barra y borne-off, más utilidades de validación."""
    # pylint: disable=too-many-public-methods

    def __init__(self) -> None:
        self.__points__: List[List[str]] = [[] for _ in range(NUM_POINTS)]
        self.__bar_map__: Dict[str, List[str]] = {BLANCO: [], NEGRO: []}
        self.__borne_off_map__: Dict[str, List[str]] = {BLANCO: [], NEGRO: []}
        # Exponer alias esperados por los tests
        self.__posiciones__ = self.__points__
        self.__barra__ = self.__bar_map__
        self.__fichas_fuera__ = self.__borne_off_map__
        self.reset_to_start()

    def reset_to_start(self) -> None:
        """Coloca las fichas en posiciones estándar de inicio."""
        # Reemplazar contenido en lugar de re-binder para mantener alias válidos
        self.__points__[:] = [[] for _ in range(NUM_POINTS)]
        self.__bar_map__.clear()
        self.__bar_map__[BLANCO] = []
        self.__bar_map__[NEGRO] = []
        self.__borne_off_map__.clear()
        self.__borne_off_map__[BLANCO] = []
        self.__borne_off_map__[NEGRO] = []

        self.__points__[0]  = [BLANCO] * 2
        self.__points__[11] = [BLANCO] * 5
        self.__points__[16] = [BLANCO] * 3
        self.__points__[18] = [BLANCO] * 5
        # Negras
        self.__points__[23] = [NEGRO] * 2
        self.__points__[12] = [NEGRO] * 5
        self.__points__[7]  = [NEGRO] * 3
        self.__points__[5]  = [NEGRO] * 5

    def stack_at(self, index: int) -> List[str]:
        """Copia de la pila en el punto `index` (0..23)."""
        self._require_point(index)
        return list(self.__points__[index])

    def bar(self, color: Optional[str] = None) -> Dict[str, List[str]] | List[str]:  # pylint: disable=disallowed-name
        """Copia de la(s) barra(s)."""
        if color is None:
            return {c: list(p) for c, p in self.__bar_map__.items()}
        self._require_color(color)
        return list(self.__bar_map__[color])

    def borne_off(self, color: Optional[str] = None) -> Dict[str, List[str]] | List[str]:
        """Copia de las fichas borneadas."""
        if color is None:
            return {c: list(p) for c, p in self.__borne_off_map__.items()}
        self._require_color(color)
        return list(self.__borne_off_map__[color])

    def bar_count(self, color: str) -> int:
        """Cantidad de fichas en la barra para el color dado."""
        self._require_color(color)
        return len(self.__bar_map__[color])

    def borne_off_count(self, color: str) -> int:
        """Cantidad de fichas borneadas (fuera) para el color dado."""
        self._require_color(color)
        return len(self.__borne_off_map__[color])

    def point_count(self, index: int) -> int:
        """Cantidad de fichas en el punto indicado (0..23)."""
        self._require_point(index)
        return len(self.__points__[index])

    def top_color_at(self, index: int) -> Optional[str]:
        """Color del tope en el punto, o None si vacío."""
        self._require_point(index)
        return self.__points__[index][-1] if self.__points__[index] else None

    def points_snapshot(self) -> List[dict]:
        """Resumen compacto de puntos (para UI/logs)."""
        out = []
        for pile in self.__points__:
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
        self.__points__[index].append(color)

    def remove_from_point(self, index: int) -> Optional[str]:
        """Saca y devuelve la ficha del tope del punto, o None si vacío."""
        self._require_point(index)
        if self.__points__[index]:
            return self.__points__[index].pop()
        return None

    def push_to_bar(self, color: str) -> None:
        """Envía una ficha del `color` a la barra (captura)."""
        self._require_color(color)
        self.__bar_map__[color].append(color)

    def pop_from_bar(self, color: str) -> Optional[str]:
        """Quita una ficha de la barra del `color`, o None si no hay."""
        self._require_color(color)
        if self.__bar_map__[color]:
            return self.__bar_map__[color].pop()
        return None

    def push_borne_off(self, color: str) -> None:
        """Agrega una ficha borneada (fuera) del `color`."""
        self._require_color(color)
        self.__borne_off_map__[color].append(color)

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
        destino_fichas = self.__points__[destino]
        if destino_fichas and len(destino_fichas) == 1 and destino_fichas[0] != ficha:
            capturado = self.__points__[destino].pop()
            self.push_to_bar(capturado)
        self.__points__[destino].append(ficha)

    def mover_desde_barra(self, color: str, destino: int) -> bool:
        """
        Mueve una ficha desde la barra al destino si no está bloqueado.
        Captura si hay una sola ficha rival.
        """
        self._require_color(color)
        if not self.__bar_map__[color]:
            return False
        destino_fichas = self.__points__[destino]
        # Bloqueado si hay 2+ del rival
        if destino_fichas and destino_fichas[0] != color and len(destino_fichas) > 1:
            return False

        # Sale de la barra
        self.__bar_map__[color].pop()

        # Captura si corresponde
        if destino_fichas and len(destino_fichas) == 1 and destino_fichas[0] != color:
            capturado = self.__points__[destino].pop()
            self.push_to_bar(capturado)

        self.__points__[destino].append(color)
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
            points = sum(1 for pile in self.__points__ for ch in pile if ch == c)
            bar_len = len(self.__bar_map__[c])  # evitar nombre desaconsejado
            off = len(self.__borne_off_map__[c])
            return points + bar_len + off

        if color is None:
            return count_color(BLANCO) + count_color(NEGRO)
        self._require_color(color)
        return count_color(color)

    def clone(self) -> "Board":
        """Copia profunda liviana (para simulaciones/tests)."""
        nb = Board.__new__(Board)  # evita reset_to_start
        # pylint: disable=protected-access
        nb.__points__ = [list(p) for p in self.__points__]
        nb.__bar_map__ = {c: list(p) for c, p in self.__bar_map__.items()}
        nb.__borne_off_map__ = {c: list(p) for c, p in self.__borne_off_map__.items()}
        nb.__posiciones__ = nb.__points__
        nb.__barra__ = nb.__bar_map__
        nb.__fichas_fuera__ = nb.__borne_off_map__
        return nb

    def _require_point(self, index: int) -> None:
        """Valida rango de punto (0..23)."""
        if not 0 <= index < NUM_POINTS:
            raise IndexError(f"Punto fuera de rango: {index}")

    def _require_color(self, color: str) -> None:
        """Valida color permitido."""
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
        if not 0 <= destino < NUM_POINTS:
            return False

        def bloqueado(idx: int) -> bool:
            pila = self.__points__[idx]
            return bool(pila) and pila[0] != color and len(pila) > 1

        if origen == -1:
            # Desde barra: debe haber fichas en barra y destino no bloqueado
            if not self.__bar_map__[color]:
                return False
            return not bloqueado(destino)

        # Origen en tablero
        if not 0 <= origen < NUM_POINTS:
            return False
        pila_origen = self.__points__[origen]
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
        if self.__bar_map__[color]:
            for d in tiradas:
                dest = self.calcular_destino_barra(color, d)
                if 0 <= dest < NUM_POINTS and self.es_movimiento_legal(-1, dest, color):
                    return True
            return False

        # Sin fichas en barra: buscar cualquier origen válido que pueda mover
        for origen in range(NUM_POINTS):
            pila = self.__points__[origen]
            if not pila or pila[0] != color:
                continue
            for d in tiradas:
                dest = self.calcular_destino(origen, color, d)
                if 0 <= dest < NUM_POINTS and self.es_movimiento_legal(origen, dest, color):
                    return True
        return False
