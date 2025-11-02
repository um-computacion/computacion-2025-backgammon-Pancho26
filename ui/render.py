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

    def dibujar(
        self,
        geo,
        estado,
        indice_hover: Optional[int],
        btn_tirar_rect: Optional[pygame.Rect] = None,
        seleccionado: Optional[int] = None,
        puede_tirar: bool = True,
        ganador: Optional[str] = None,  # NUEVO
    ) -> None:
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

        # Fichas capturadas en la barra central
        self.__dibujar_barra__(geo.__rect_barra__, estado)

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

        # Botón "Tirar (R)" (se dibuja gris si puede_tirar==False)
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

        # NUEVO: Overlay de ganador
        if ganador:
            # Fondo semi-transparente
            overlay = pygame.Surface(self.__pantalla__.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.__pantalla__.blit(overlay, (0, 0))
            # Cartel central
            msg = f"¡Ganó {ganador}!"
            texto = self.__fuente__.render(msg, True, (255, 255, 255))
            cx = geo.__rect_tablero__.centerx
            cy = geo.__rect_tablero__.centery
            # Marco
            box_w = max(260, texto.get_width() + 40)
            box_h = 80
            box = pygame.Rect(0, 0, box_w, box_h)
            box.center = (cx, cy)
            pygame.draw.rect(self.__pantalla__, (30, 30, 30), box, border_radius=10)
            pygame.draw.rect(self.__pantalla__, t.__marco__, box, width=2, border_radius=10)
            self.__pantalla__.blit(
                texto, (box.centerx - texto.get_width() // 2, box.centery - texto.get_height() // 2)
            )

    def __dibujar_barra__(self, rect: pygame.Rect, estado) -> None:
        """
        Dibuja las fichas capturadas en la barra central.
        Las blancas se apilan en la mitad superior y las negras en la inferior.
        """
        if estado is None:
            return
        try:
            bar_blancas = int(getattr(estado, "__bar_blancas__", 0))
        except Exception:
            bar_blancas = 0
        try:
            bar_negras = int(getattr(estado, "__bar_negras__", 0))
        except Exception:
            bar_negras = 0
        if bar_blancas <= 0 and bar_negras <= 0:
            return

        mitad_altura = rect.height // 2
        area_sup = pygame.Rect(rect.left, rect.top, rect.width, mitad_altura)
        area_inf = pygame.Rect(rect.left, rect.top + mitad_altura, rect.width, rect.height - mitad_altura)

        if bar_blancas > 0:
            self.__dibujar_pila_barra__(area_sup, bar_blancas, self.__tema__.__ficha_clara__, direccion=1)
        if bar_negras > 0:
            self.__dibujar_pila_barra__(area_inf, bar_negras, self.__tema__.__ficha_oscura__, direccion=-1)

        # Etiquetas de conteo sobre la barra (xN)
        texto_color_claro = self.__tema__.__texto__
        texto_color_oscuro = (235, 235, 235)
        if bar_blancas > 0:
            etiqueta = self.__fuente__.render(f"x{bar_blancas}", True, texto_color_claro)
            pos = etiqueta.get_rect()
            pos.midtop = (rect.centerx, area_sup.top + 4)
            self.__pantalla__.blit(etiqueta, pos)
        if bar_negras > 0:
            etiqueta = self.__fuente__.render(f"x{bar_negras}", True, texto_color_oscuro)
            pos = etiqueta.get_rect()
            pos.midbottom = (rect.centerx, area_inf.bottom - 4)
            self.__pantalla__.blit(etiqueta, pos)

    def __dibujar_pila_barra__(self, area: pygame.Rect, cantidad: int, color, direccion: int) -> None:
        """
        Dibuja una pila vertical de fichas en el área indicada.
        `direccion` controla si se apilan hacia abajo (+1) o hacia arriba (-1).
        """
        if cantidad <= 0:
            return
        margen = 12
        altura_util = max(12.0, area.height - 2 * margen)
        radio = min(area.width * 0.4, altura_util / max(cantidad, 1) * 0.45)
        radio = max(8.0, min(radio, area.width * 0.45))
        # Paso entre centros; ajustar para que quepan dentro del área
        paso_default = 2 * radio + max(2.0, radio * 0.25)
        if cantidad > 1:
            max_span = max(0.0, altura_util - 2 * radio)
            paso_fit = max_span / (cantidad - 1) if max_span > 0 else radio * 0.8
            paso = min(paso_default, paso_fit)
        else:
            paso = 0.0

        if direccion > 0:
            centro_y = area.top + margen + radio
        else:
            centro_y = area.bottom - margen - radio

        limite_superior = area.top + margen + radio
        limite_inferior = area.bottom - margen - radio
        centro_x = area.centerx
        for i in range(cantidad):
            cy = centro_y + direccion * i * paso
            cy = max(limite_superior, min(limite_inferior, cy))
            pygame.draw.circle(self.__pantalla__, color, (int(centro_x), int(round(cy))), int(round(radio)))
            pygame.draw.circle(
                self.__pantalla__,
                self.__tema__.__borde_ficha__,
                (int(centro_x), int(round(cy))),
                int(round(radio)),
                width=2,
            )
