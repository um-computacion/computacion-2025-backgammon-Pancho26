"""
Renderizador del tablero con Pygame.
"""

from typing import Optional
import pygame
from ui.theme import TemaTablero


class RenderizadorTablero:
    """
    Dibuja tablero, puntas, fichas y resaltados.

    Atributos:
        self.__pantalla__ (pygame.Surface): Superficie destino.
        self.__fuente__ (pygame.font.Font): Fuente para etiquetas.
        self.__tema__ (TemaTablero): Paleta de colores.
    """

    def __init__(self, pantalla: pygame.Surface, fuente: pygame.font.Font, tema: TemaTablero) -> None:
        """
        Inicializa el renderizador.

        Parámetros:
            pantalla (pygame.Surface): Superficie de dibujo.
            fuente (pygame.font.Font): Fuente para textos.
            tema (TemaTablero): Tema de colores.

        Retorna:
            None
        """
        self.__pantalla__ = pantalla
        self.__fuente__ = fuente
        self.__tema__ = tema

    def dibujar(self, geo, estado, indice_hover: Optional[int], btn_tirar_rect: Optional[pygame.Rect] = None, seleccionado: Optional[int] = None, puede_tirar: bool = True) -> None:
        """
        Dibuja el tablero completo.

        Parámetros:
            geo: Objeto de geometría con atributos:
                 __rect_tablero__, __rect_barra__, __triangulos__, __etiquetas__,
                 __colores_puntas__, __altura_triangulo__, __ancho_punta__.
            estado: Objeto de estado con listas __blancas__ y __negras__ (índices 1..24).
            indice_hover (Optional[int]): Índice de triángulo bajo el puntero o None.
            btn_tirar_rect (Optional[pygame.Rect]): Rectángulo para dibujar el botón "Tirar (R)".

        Retorna:
            None
        """
        t = self.__tema__
        # Fondo y marco
        self.__pantalla__.fill(t.__fondo__)
        pygame.draw.rect(self.__pantalla__, t.__marco__, geo.__rect_tablero__.inflate(16, 16), border_radius=10)
        pygame.draw.rect(self.__pantalla__, t.__madera__, geo.__rect_tablero__, border_radius=6)
        pygame.draw.rect(self.__pantalla__, t.__barra__, geo.__rect_barra__)

        # Puntas
        for i, tri in enumerate(geo.__triangulos__):
            pygame.draw.polygon(self.__pantalla__, geo.__colores_puntas__[i], tri)

        # Resalte de hover
        if indice_hover is not None and 0 <= indice_hover < len(geo.__triangulos__):
            pygame.draw.polygon(self.__pantalla__, t.__resalte__, geo.__triangulos__[indice_hover], width=3)

        # NUEVO: resaltar punta seleccionada (por etiqueta 1..24)
        if seleccionado is not None:
            try:
                idx_sel = next(i for i, lab in enumerate(geo.__etiquetas__) if lab == seleccionado)
                pygame.draw.polygon(self.__pantalla__, (0, 180, 255), geo.__triangulos__[idx_sel], width=4)
            except StopIteration:
                pass

        # Línea separadora central
        pygame.draw.line(
            self.__pantalla__,
            t.__madera_oscura__,
            (geo.__rect_tablero__.left, geo.__rect_tablero__.centery),
            (geo.__rect_tablero__.right, geo.__rect_tablero__.centery),
            2,
        )

        # Cálculo de apilado de fichas
        max_blancas = max(estado.__blancas__[1:]) if any(estado.__blancas__[1:]) else 0
        max_negras = max(estado.__negras__[1:]) if any(estado.__negras__[1:]) else 0
        pila_max = max(max_blancas, max_negras)

        margen_etiqueta = self.__fuente__.get_height() + 6
        alto_util = max(10.0, geo.__altura_triangulo__ - margen_etiqueta - 6)
        radio = min(geo.__ancho_punta__ * 0.45, alto_util / max(1, pila_max) * 0.45)
        radio = max(8.0, radio)
        espacio = max(2.0, radio * 0.12)
        paso = 2 * radio + espacio

        # Fichas (se muestra color dominante por punto)
        for i, tri in enumerate(geo.__triangulos__):
            (x1, y1), (x2, y2), (x3, y3) = tri
            base_y = (y1 + y2) / 2.0
            centro_x = (x1 + x2) / 2.0
            es_superior = y1 < y3

            etiqueta = geo.__etiquetas__[i]
            b = estado.__blancas__[etiqueta]
            n = estado.__negras__[etiqueta]
            if b == 0 and n == 0:
                continue

            cantidad = b if b >= n else n
            color = t.__ficha_clara__ if b >= n else t.__ficha_oscura__
            inicio_y = base_y + (margen_etiqueta + radio) if es_superior else base_y - (margen_etiqueta + radio)
            direccion = 1 if es_superior else -1

            for k in range(cantidad):
                cy = inicio_y + direccion * (k * paso)
                pygame.draw.circle(self.__pantalla__, color, (int(centro_x), int(cy)), int(radio))
                pygame.draw.circle(self.__pantalla__, t.__borde_ficha__, (int(centro_x), int(cy)), int(radio), width=2)

        # Etiquetas numéricas de puntos
        for i, tri in enumerate(geo.__triangulos__):
            texto = self.__fuente__.render(str(geo.__etiquetas__[i]), True, t.__texto__)
            (x1, y1), (x2, y2), (x3, y3) = tri
            base_y = (y1 + y2) / 2.0
            es_superior = y1 < y3
            pos = (
                x1 + (x2 - x1) / 2.0 - texto.get_width() / 2.0,
                base_y + 6 if es_superior else base_y - texto.get_height() - 6,
            )
            self.__pantalla__.blit(texto, pos)

        # NUEVO: dibujar dados y movimientos restantes sobre la barra central
        try:
            d1, d2 = getattr(estado, "__dados__", (0, 0))
            restantes = getattr(estado, "__movimientos_pendientes__", [])
            bar_b = int(getattr(estado, "__bar_blancas__", 0))
            bar_n = int(getattr(estado, "__bar_negras__", 0))
            fuera_b = int(getattr(estado, "__fuera_blancas__", 0))
            fuera_n = int(getattr(estado, "__fuera_negras__", 0))
        except Exception:
            d1, d2, restantes = 0, 0, []
            bar_b = bar_n = fuera_b = fuera_n = 0

        barra = geo.__rect_barra__
        size = max(36, min(64, int(barra.width * 0.8)))
        pad = 10
        total_w = size * 2 + pad
        x0 = int(barra.centerx - total_w / 2)
        y0 = int(geo.__rect_tablero__.top + 10)

        def draw_die(x: int, y: int, n: int) -> None:
            rect = pygame.Rect(x, y, size, size)
            pygame.draw.rect(self.__pantalla__, (245, 245, 245), rect, border_radius=6)
            pygame.draw.rect(self.__pantalla__, self.__tema__.__marco__, rect, width=2, border_radius=6)
            txt = self.__fuente__.render(str(n), True, (20, 20, 20))
            self.__pantalla__.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # Fondo sutil detrás de los dados
        back_h = size + 40
        back_rect = pygame.Rect(x0 - 8, y0 - 6, total_w + 16, back_h + 12)
        pygame.draw.rect(self.__pantalla__, (0, 0, 0), back_rect, width=1, border_radius=8)

        if d1 > 0 and d2 > 0:
            draw_die(x0, y0, d1)
            draw_die(x0 + size + pad, y0, d2)
        info = f"Restantes: {restantes}" if restantes else "Sin restantes"

        # NUEVO: pilas en barra (superior=blancas, inferior=negras)
        def draw_bar_stack(area: pygame.Rect, count: int, color: tuple[int, int, int], arriba: bool) -> None:
            if count <= 0:
                return
            r = min(area.width * 0.45, area.height / max(1, count) * 0.45)
            r = max(7.0, r)
            espacio = max(2.0, r * 0.12)
            paso = 2 * r + espacio
            cx = area.centerx
            cy0 = area.top + r + 4 if arriba else area.bottom - r - 4
            dir_y = 1 if arriba else -1
            for k in range(count):
                cy = cy0 + dir_y * (k * paso)
                if cy < area.top + r or cy > area.bottom - r:
                    break
                pygame.draw.circle(self.__pantalla__, color, (int(cx), int(cy)), int(r))
                pygame.draw.circle(self.__pantalla__, self.__tema__.__borde_ficha__, (int(cx), int(cy)), int(r), width=2)

        mitad_sup = pygame.Rect(barra.left, barra.top + 4, barra.width, barra.height // 2 - 8)
        mitad_inf = pygame.Rect(barra.left, barra.centery + 4, barra.width, barra.height // 2 - 8)
        draw_bar_stack(mitad_sup, bar_b, self.__tema__.__ficha_clara__, True)   # Blancas arriba
        draw_bar_stack(mitad_inf, bar_n, self.__tema__.__ficha_oscura__, False) # Negras abajo

        # Texto de estado bajo los dados: Restantes + Barra + Fuera
        linea1 = info
        linea2 = f"Barra B/N: {bar_b}/{bar_n}  |  Fuera B/N: {fuera_b}/{fuera_n}"
        info1 = self.__fuente__.render(linea1, True, self.__tema__.__texto__)
        info2 = self.__fuente__.render(linea2, True, self.__tema__.__texto__)
        self.__pantalla__.blit(info1, (barra.centerx - info1.get_width() // 2, y0 + size + 6))
        self.__pantalla__.blit(info2, (barra.centerx - info2.get_width() // 2, y0 + size + 6 + info1.get_height()))

        # NUEVO: botón "Tirar (R)" con estado habilitado/deshabilitado
        if btn_tirar_rect is not None:
            fill = (255, 215, 0) if puede_tirar else (150, 150, 150)
            pygame.draw.rect(self.__pantalla__, fill, btn_tirar_rect, border_radius=8)
            pygame.draw.rect(self.__pantalla__, self.__tema__.__marco__, btn_tirar_rect, width=2, border_radius=8)
            label_color = (20, 20, 20) if puede_tirar else (60, 60, 60)
            label = self.__fuente__.render("Tirar (R)", True, label_color)
            self.__pantalla__.blit(
                label,
                (btn_tirar_rect.centerx - label.get_width() // 2, btn_tirar_rect.centery - label.get_height() // 2),
            )