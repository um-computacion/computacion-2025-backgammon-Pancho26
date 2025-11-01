"""
Controlador de la UI con Pygame: eventos, redimensionado y loop principal.
"""

from typing import Optional, Any
import pygame
import random

from ui.theme import TemaTablero
import ui.geometry as geometry
from ui.hit_test import DeteccionPuntas
from ui.render import RenderizadorTablero


class ControladorUI:
    """
    Orquesta Pygame: maneja eventos, reconstruye geometría y dibuja cada frame.

    Atributos:
        self.__pantalla__ (pygame.Surface): Superficie de render.
        self.__reloj__ (pygame.time.Clock): Control de FPS.
        self.__fuente__ (pygame.font.Font): Fuente para textos.
        self.__fps__ (int): Cuadros por segundo.
        self.__tema__ (TemaTablero): Paleta de colores.
        self.__layout__ (MotorDisposicion): Motor de disposición.
        self.__geo__ (GeometriaTablero): Geometría actual.
        self.__deteccion__ (DeteccionPuntas): Detección de puntas.
        self.__render__ (RenderizadorTablero): Renderizador.
        self.__estado__ (Any): Estado del juego (debe exponer __blancas__, __negras__).
        self.__indice_hover__ (Optional[int]): Índice de punta bajo el mouse.
    """

    def __init__(
        self,
        ancho: int = 1000,
        alto: int = 700,
        estado: Optional[Any] = None,
        fps: int = 60,
        titulo: str = "Backgammon - Tablero",
    ) -> None:
        """
        Inicializa Pygame y dependencias de UI.

        Parámetros:
            ancho (int): Ancho de la ventana.
            alto (int): Alto de la ventana.
            estado (Any|None): Estado del juego con __blancas__/__negras__ (opcional).
            fps (int): Cuadros por segundo.
            titulo (str): Título de la ventana.

        Retorna:
            None
        """
        pygame.init()
        pygame.display.set_caption(titulo)
        self.__pantalla__ = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
        self.__reloj__ = pygame.time.Clock()
        self.__fuente__ = pygame.font.SysFont(None, 20)
        self.__fps__ = fps

        self.__tema__ = TemaTablero()
        self.__overlay_margin_top__ = 12
        self.__overlay_spacing__ = 8
        self.__overlay_height__ = 120
        self.__overlay_offset__ = (
            self.__overlay_margin_top__ + self.__overlay_height__ + self.__overlay_spacing__
        )
        self.__layout__ = geometry.MotorDisposicion(margen=20, fraccion_barra=0.06)
        self.__geo__: geometry.GeometriaTablero = self.__layout__.construir(
            ancho,
            alto,
            self.__tema__.__punta_a__,
            self.__tema__.__punta_b__,
            self.__tema__.__barra__,
            offset_superior=self.__overlay_offset__,
        )
        self.__deteccion__ = DeteccionPuntas(self.__geo__.__triangulos__)
        self.__render__ = RenderizadorTablero(self.__pantalla__, self.__fuente__, self.__tema__)
        self.__estado__ = estado  # se inyecta desde la capa de juego
        self.__indice_hover__: Optional[int] = None
        # NUEVO: rect del botón "Tirar"
        self.__btn_tirar__: pygame.Rect = self.__calc_rect_boton_tirar__()
        # NUEVO: botón "Pasar (P)"
        self.__btn_pasar__: pygame.Rect = self.__calc_rect_boton_pasar__()
        # NUEVO: botón "Sacar (S)"
        self.__btn_sacar__: pygame.Rect = self.__calc_rect_boton_sacar__()
        # NUEVO: selección de origen (punto 1..24)
        self.__seleccion_origen__: Optional[int] = None
        # NUEVO: ganador actual (None si no hay)
        self.__ganador__: Optional[str] = None

    def __calc_rect_boton_tirar__(self) -> pygame.Rect:
        """
        Calcula el rect del botón 'Tirar (R)' en función de la geometría actual.
        """
        barra = self.__geo__.__rect_barra__
        w = max(110, min(180, int(barra.width * 0.9)))
        h = 36
        x = int(barra.centerx - w / 2)
        y = int(barra.bottom - h - 12)
        return pygame.Rect(x, y, w, h)

    def __calc_rect_boton_pasar__(self) -> pygame.Rect:
        """
        Calcula el rect del botón 'Pasar (P)' ubicado sobre el botón 'Tirar'.
        """
        barra = self.__geo__.__rect_barra__
        w = max(110, min(180, int(barra.width * 0.9)))
        h = 36
        ref = getattr(self, "__btn_tirar__", None)
        x = int(barra.centerx - w / 2)
        if isinstance(ref, pygame.Rect):
            y = int(ref.top - h - 8)
        else:
            y = int(barra.bottom - (2 * h) - 20)
        return pygame.Rect(x, y, w, h)

    # NUEVO: rect del botón 'Sacar (S)' posicionado sobre el botón 'Tirar'
    def __calc_rect_boton_sacar__(self) -> pygame.Rect:
        barra = self.__geo__.__rect_barra__
        w = max(110, min(180, int(barra.width * 0.9)))
        h = 36
        # Ubicar encima del botón tirar con un margen
        ref = getattr(self, "__btn_pasar__", None)
        x = int(barra.centerx - w / 2)
        if isinstance(ref, pygame.Rect):
            y = int(ref.top - h - 8)
        else:
            y = int(barra.bottom - (2 * h) - 20)
        return pygame.Rect(x, y, w, h)

    def __redimensionar__(self, nuevo_ancho: int, nuevo_alto: int) -> None:
        """
        Reconstruye la geometría y superficie al redimensionar.

        Parámetros:
            nuevo_ancho (int): Ancho nuevo.
            nuevo_alto (int): Alto nuevo.

        Retorna:
            None
        """
        self.__pantalla__ = pygame.display.set_mode((nuevo_ancho, nuevo_alto), pygame.RESIZABLE)
        self.__geo__ = self.__layout__.construir(
            nuevo_ancho,
            nuevo_alto,
            self.__tema__.__punta_a__,
            self.__tema__.__punta_b__,
            self.__tema__.__barra__,
            offset_superior=self.__overlay_offset__,
        )
        self.__deteccion__.actualizar_triangulos(self.__geo__.__triangulos__)
        # NUEVO: actualizar rects de botones al redimensionar
        self.__btn_tirar__ = self.__calc_rect_boton_tirar__()
        self.__btn_pasar__ = self.__calc_rect_boton_pasar__()
        self.__btn_sacar__ = self.__calc_rect_boton_sacar__()

    def __tirar_dados__(self) -> None:
        """
        Tira dos dados y los setea en el estado, si es posible.
        """
        # Bloquear si ya hay ganador
        if self.__ganador__ is not None:
            print("La partida terminó. Reinicie para jugar de nuevo.")
            return
        # NUEVO: bloquear si hay movimientos pendientes
        if self.__estado__ is not None and hasattr(self.__estado__, "hay_movimientos"):
            try:
                if self.__estado__.hay_movimientos():
                    print("Primero usá los movimientos pendientes antes de volver a tirar.")
                    return
            except Exception:
                pass
        if self.__estado__ is not None and hasattr(self.__estado__, "set_dados"):
            d1, d2 = random.randint(1, 6), random.randint(1, 6)
            try:
                self.__estado__.set_dados(d1, d2)
                print(f"Dados: {d1},{d2}  Restantes: {getattr(self.__estado__, '__movimientos_pendientes__', [])}")
            except Exception as ex:
                print(f"No se pudo setear dados: {ex}")

    # NUEVO: helpers de selección/movimiento
    def __turno_actual__(self) -> str:
        return getattr(self.__estado__, "__turno__", "BLANCAS")

    def __tiene_ficha_del_turno__(self, punto: int) -> bool:
        if self.__estado__ is None:
            return False
        t = self.__turno_actual__()
        if t == "BLANCAS":
            return getattr(self.__estado__, "__blancas__", [0] * 25)[punto] > 0
        return getattr(self.__estado__, "__negras__", [0] * 25)[punto] > 0

    def __calcular_pasos__(self, desde: int, destino: int) -> Optional[int]:
        t = self.__turno_actual__()
        dir_val = -1 if t == "BLANCAS" else +1
        pasos = (destino - desde) * dir_val
        return pasos if pasos > 0 else None

    def __hay_movimientos__(self) -> bool:
        try:
            return bool(self.__estado__.hay_movimientos())  # type: ignore[attr-defined]
        except Exception:
            # Fallback a lista interna
            restantes = getattr(self.__estado__, "__movimientos_pendientes__", [])
            return bool(restantes)

    # NUEVO: utilidades de captura y victoria
    def __evaluar_ganador__(self) -> None:
        """
        Si algún jugador llegó a 15 fichas fuera, fija __ganador__.
        """
        b = getattr(self.__estado__, "__fuera_blancas__", 0)
        n = getattr(self.__estado__, "__fuera_negras__", 0)
        if b >= 15:
            self.__ganador__ = "BLANCAS"
        elif n >= 15:
            self.__ganador__ = "NEGRAS"

    # NUEVO: obtener dados a mostrar (pendientes o última tirada)
    def __dados_visibles__(self) -> list[int]:
        """
        Retorna una lista de valores de dados para mostrar en pantalla.
        - Si hay movimientos pendientes, se muestran esos valores (incluye dobles).
        - Si no, se intenta mostrar la última tirada (__dados__), ignorando ceros.
        """
        if self.__estado__ is None:
            return []
        # Primero, movimientos pendientes
        try:
            pendientes = list(getattr(self.__estado__, "__movimientos_pendientes__", []))
            if pendientes:
                return pendientes
        except Exception:
            pass
        # Fallback: última tirada (__dados__ = (d1, d2))
        try:
            d1, d2 = getattr(self.__estado__, "__dados__", (0, 0))
            vals = [v for v in (int(d1), int(d2)) if 1 <= v <= 6]
            return vals
        except Exception:
            return []

    # NUEVO: overlay de dados (siempre por encima del tablero)
    def __dibujar_dados_overlay__(self) -> None:
        """
        Dibuja panel superior con turno actual, dados y estado de fichas fuera.
        """
        if self.__estado__ is None:
            return

        surface = self.__pantalla__
        ancho, _ = surface.get_size()
        vals = self.__dados_visibles__()
        turno_raw = getattr(self.__estado__, "__turno__", "BLANCAS")
        turno_txt = str(turno_raw).upper()
        es_blancas = turno_txt.startswith("BLA")

        margin = self.__overlay_margin_top__
        overlay_height = self.__overlay_height__
        overlay_rect = pygame.Rect(margin, margin, ancho - 2 * margin, overlay_height)
        bg_color = (246, 246, 232) if es_blancas else (60, 70, 110)
        border_color = (172, 162, 128) if es_blancas else (32, 36, 70)
        text_color = (40, 40, 40) if es_blancas else (235, 235, 245)
        pygame.draw.rect(surface, bg_color, overlay_rect, border_radius=14)
        pygame.draw.rect(surface, border_color, overlay_rect, width=2, border_radius=14)

        # Texto de turno
        turno_label = self.__fuente__.render(f"Turno: {turno_txt.capitalize()}", True, text_color)
        surface.blit(turno_label, (overlay_rect.left + 16, overlay_rect.top + 10))

        # Dados en el centro
        dados_size = 32
        gap = 12
        dados_y = overlay_rect.top + 44
        if vals:
            total_width = len(vals) * dados_size + (len(vals) - 1) * gap
            dados_x = max(overlay_rect.left + 24, overlay_rect.centerx - total_width // 2)
            for i, v in enumerate(vals):
                rect = pygame.Rect(dados_x + i * (dados_size + gap), dados_y, dados_size, dados_size)
                pygame.draw.rect(surface, (250, 250, 212), rect, border_radius=6)
                pygame.draw.rect(surface, (30, 30, 30), rect, width=2, border_radius=6)
                numero = self.__fuente__.render(str(v), True, (30, 30, 30))
                surface.blit(numero, numero.get_rect(center=rect.center))
        else:
            aviso = self.__fuente__.render("Tirá los dados para comenzar.", True, text_color)
            surface.blit(aviso, aviso.get_rect(midtop=(overlay_rect.centerx, dados_y + 4)))

        # Paneles de fichas borneadas
        try:
            fuera_b = int(getattr(self.__estado__, "__fuera_blancas__", 0))
            fuera_n = int(getattr(self.__estado__, "__fuera_negras__", 0))
        except Exception:
            fuera_b = fuera_n = 0

        panel_height = 36
        panel_gap = 14
        panel_y = overlay_rect.bottom - panel_height - 12
        panel_width = (overlay_rect.width - 3 * panel_gap) // 2
        panel_blancas = pygame.Rect(overlay_rect.left + panel_gap, panel_y, panel_width, panel_height)
        panel_negras = pygame.Rect(panel_blancas.right + panel_gap, panel_y, panel_width, panel_height)

        self.__dibujar_panel_borne__(panel_blancas, "Blancas", fuera_b, 15, True)
        self.__dibujar_panel_borne__(panel_negras, "Negras", fuera_n, 15, False)

    def __dibujar_panel_borne__(self, rect: pygame.Rect, etiqueta: str, cantidad: int, total: int, es_blancas: bool) -> None:
        """Panel visual para fichas borneadas."""
        base_color = (244, 241, 221) if es_blancas else (50, 55, 88)
        borde = (168, 160, 120) if es_blancas else (28, 30, 52)
        texto_color = (40, 40, 40) if es_blancas else (235, 235, 242)
        barra_color = (206, 198, 158) if es_blancas else (80, 90, 130)
        progreso_color = self.__tema__.__ficha_clara__ if es_blancas else self.__tema__.__ficha_oscura__

        pygame.draw.rect(self.__pantalla__, base_color, rect, border_radius=10)
        pygame.draw.rect(self.__pantalla__, borde, rect, width=2, border_radius=10)

        titulo = self.__fuente__.render(f"Fuera {etiqueta}", True, texto_color)
        conteo = self.__fuente__.render(f"{cantidad}/{total}", True, texto_color)
        self.__pantalla__.blit(titulo, (rect.left + 10, rect.top + 6))
        self.__pantalla__.blit(conteo, (rect.right - conteo.get_width() - 10, rect.top + 6))

        barra_rect = pygame.Rect(rect.left + 10, rect.bottom - 16, rect.width - 20, 8)
        pygame.draw.rect(self.__pantalla__, barra_color, barra_rect, border_radius=4)
        razon = 0.0 if total <= 0 else min(max(cantidad / total, 0.0), 1.0)
        fill_w = int(barra_rect.width * razon)
        if fill_w > 0:
            lleno = pygame.Rect(barra_rect.left, barra_rect.top, fill_w, barra_rect.height)
            pygame.draw.rect(self.__pantalla__, progreso_color, lleno, border_radius=4)
        pygame.draw.rect(self.__pantalla__, borde, barra_rect, width=1, border_radius=4)

    # NUEVO: dibuja el botón 'Pasar (P)' como overlay
    def __dibujar_boton_pasar_overlay__(self) -> None:
        rect = self.__btn_pasar__
        enabled = self.__puede_pasar_turno__()
        surface = self.__pantalla__
        bg = (200, 170, 60) if enabled else (150, 150, 150)
        border = (40, 40, 40)
        txt = (15, 15, 15)
        pygame.draw.rect(surface, bg, rect, border_radius=8)
        pygame.draw.rect(surface, border, rect, width=2, border_radius=8)
        label = self.__fuente__.render("Pasar (P)", True, txt)
        surface.blit(label, label.get_rect(center=rect.center))

    # NUEVO: dibuja el botón 'Sacar (S)' como overlay encima de todo
    def __dibujar_boton_sacar_overlay__(self) -> None:
        rect = self.__btn_sacar__
        enabled = self.__puede_sacar__()
        surface = self.__pantalla__
        # Colores de alto contraste
        bg = (80, 170, 90) if enabled else (150, 150, 150)
        border = (20, 20, 20)
        txt = (10, 10, 10)
        pygame.draw.rect(surface, bg, rect, border_radius=8)
        pygame.draw.rect(surface, border, rect, width=2, border_radius=8)
        label = self.__fuente__.render("Sacar (S)", True, txt)
        surface.blit(label, label.get_rect(center=rect.center))

    def __procesar_evento__(self, evento: pygame.event.Event) -> bool:
        """
        Procesa un evento de Pygame.

        Parámetros:
            evento (pygame.event.Event): Evento a procesar.

        Retorna:
            bool: False para salir del loop, True para continuar.
        """
        if evento.type == pygame.QUIT:
            return False
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return False
        # Si hay ganador, ignorar clicks/teclas (salvo ESC/QUIT)
        if self.__ganador__ is not None:
            return True
        # NUEVO: atajo 'S' para sacar borne-off
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_s:
            self.__intentar_sacar__()
        # NUEVO: atajo 'P' para pasar turno
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_p:
            self.__intentar_pasar_turno__()
        # NUEVO: tirar dados con 'R'
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            self.__tirar_dados__()
        if evento.type == pygame.VIDEORESIZE:
            self.__redimensionar__(evento.w, evento.h)
        elif evento.type == pygame.MOUSEMOTION:
            self.__indice_hover__ = self.__deteccion__.buscar_indice_punta(evento.pos)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            # NUEVO: click en botón 'Sacar'
            if self.__btn_sacar__.collidepoint(evento.pos):
                self.__intentar_sacar__()
                return True
            # NUEVO: click en botón 'Pasar'
            if self.__btn_pasar__.collidepoint(evento.pos):
                self.__intentar_pasar_turno__()
                return True
            # Click en botón 'Tirar'
            if self.__btn_tirar__.collidepoint(evento.pos):
                self.__tirar_dados__()
                return True

            if self.__estado__ is None:
                return True

            idx = self.__deteccion__.buscar_indice_punta(evento.pos)
            if idx is None:
                return True
            etiqueta = self.__geo__.__etiquetas__[idx]  # punto 1..24
            turno = self.__turno_actual__()

            # NUEVO: si hay fichas en barra, sólo reingreso
            bar_b = getattr(self.__estado__, "__bar_blancas__", 0)
            bar_n = getattr(self.__estado__, "__bar_negras__", 0)
            if (turno == "BLANCAS" and bar_b > 0) or (turno == "NEGRAS" and bar_n > 0):
                # Click en punta válida de entrada
                if turno == "BLANCAS" and 19 <= etiqueta <= 24:
                    pasos = 25 - etiqueta
                    if getattr(self.__estado__, "puede_reingresar", lambda _p: False)(pasos):
                        getattr(self.__estado__, "reingresar")(pasos)
                        self.__seleccion_origen__ = None
                    else:
                        print("Reingreso inválido con ese dado/entrada.")
                elif turno == "NEGRAS" and 1 <= etiqueta <= 6:
                    pasos = etiqueta
                    if getattr(self.__estado__, "puede_reingresar", lambda _p: False)(pasos):
                        getattr(self.__estado__, "reingresar")(pasos)
                        self.__seleccion_origen__ = None
                    else:
                        print("Reingreso inválido con ese dado/entrada.")
                # Tras reingresar, evaluar ganador
                self.__evaluar_ganador__()
                return True

            # Si no hay dados, pedir tirar primero
            if not self.__hay_movimientos__():
                print("Tirá los dados (R o botón) antes de mover.")
                return True

            # Selección de origen/destino
            if self.__seleccion_origen__ is None:
                if self.__tiene_ficha_del_turno__(etiqueta):
                    self.__seleccion_origen__ = etiqueta
                else:
                    print("Seleccioná una punta que tenga una ficha tuya.")
            else:
                desde = self.__seleccion_origen__
                if etiqueta == desde:
                    # toggle selección
                    self.__seleccion_origen__ = None
                    return True

                pasos = self.__calcular_pasos__(desde, etiqueta)
                pendientes = list(getattr(self.__estado__, "__movimientos_pendientes__", []))
                if pasos is not None and pasos in pendientes:
                    if getattr(self.__estado__, "puede_mover", lambda d, p: False)(desde, pasos):
                        try:
                            # NUEVO: snapshot de barra rival para detectar captura
                            oponente = "BLANCAS" if turno == "NEGRAS" else "NEGRAS"
                            bar_rival_antes = getattr(self.__estado__, "__bar_blancas__" if oponente == "BLANCAS" else "__bar_negras__", 0)
                            getattr(self.__estado__, "mover")(desde, pasos)
                            self.__seleccion_origen__ = None
                            # Mensaje de captura si la barra rival aumentó
                            bar_rival_desp = getattr(self.__estado__, "__bar_blancas__" if oponente == "BLANCAS" else "__bar_negras__", 0)
                            if bar_rival_desp > bar_rival_antes:
                                print("¡Captura! Comiste una ficha rival.")
                            # Evaluar ganador tras mover
                            self.__evaluar_ganador__()
                        except Exception as ex:
                            print(f"No se pudo mover: {ex}")
                    else:
                        print("Movimiento inválido para los dados actuales.")
                else:
                    # Permitir cambiar de origen si clickeó otra punta propia
                    if self.__tiene_ficha_del_turno__(etiqueta):
                        self.__seleccion_origen__ = etiqueta
                    else:
                        print("El destino no coincide con ningún dado disponible.")
        return True

    # NUEVO: pasos para borne-off desde un punto según turno (sin validar reglas)
    def __pasos_borne_off__(self, desde: int) -> Optional[int]:
        t = self.__turno_actual__()
        if t == "BLANCAS":
            # Casa: 1..6, distancia exacta hasta salir (0) = desde
            return desde if 1 <= desde <= 6 else None
        # NEGRAS: casa 19..24, distancia exacta hasta 25 = 25 - desde
        return (25 - desde) if 19 <= desde <= 24 else None

    def __puede_pasar_turno__(self) -> bool:
        if self.__estado__ is None:
            return False
        fn = getattr(self.__estado__, "puede_saltear_turno", None)
        if callable(fn):
            try:
                return bool(fn())
            except Exception:
                return False
        return False

    # NUEVO: verifica si actualmente se puede "sacar" la ficha seleccionada
    def __puede_sacar__(self) -> bool:
        if self.__estado__ is None or self.__seleccion_origen__ is None:
            return False
        try:
            pasos = self.__pasos_borne_off__(self.__seleccion_origen__)
            if pasos is None:
                return False
            pendientes = list(getattr(self.__estado__, "__movimientos_pendientes__", []))
            if pasos not in pendientes:
                return False
            # Validación completa delegada al estado
            return bool(getattr(self.__estado__, "puede_mover", lambda d, p: False)(self.__seleccion_origen__, pasos))
        except Exception:
            return False

    # NUEVO: intentar ejecutar el borneo (click botón o tecla S)
    def __intentar_sacar__(self) -> None:
        if self.__ganador__ is not None or self.__estado__ is None:
            return
        # Requiere tener dados y un origen seleccionado
        if not self.__hay_movimientos__():
            print("No hay dados disponibles para sacar. Tirá primero.")
            return
        if self.__seleccion_origen__ is None:
            print("Seleccioná una punta en tu casa para sacar.")
            return
        pasos = self.__pasos_borne_off__(self.__seleccion_origen__)
        if pasos is None:
            print("Ese punto no pertenece a tu casa.")
            return
        try:
            if getattr(self.__estado__, "puede_mover", lambda d, p: False)(self.__seleccion_origen__, pasos):
                getattr(self.__estado__, "mover")(self.__seleccion_origen__, pasos)
                self.__seleccion_origen__ = None
                # Evaluar ganador tras bornear
                self.__evaluar_ganador__()
            else:
                print("No podés sacar con los dados actuales.")
        except Exception as ex:
            print(f"No se pudo sacar: {ex}")

    # NUEVO: intentar pasar el turno manualmente
    def __intentar_pasar_turno__(self) -> None:
        if self.__ganador__ is not None or self.__estado__ is None:
            return
        fn = getattr(self.__estado__, "saltear_turno", None)
        if not callable(fn):
            print("El estado actual no soporta pasar turno.")
            return
        try:
            if fn():
                self.__seleccion_origen__ = None
                print(f"Turno de {self.__turno_actual__()}.")
            else:
                print("Aún hay movimientos posibles; no se puede pasar.")
        except Exception as ex:
            print(f"No se pudo pasar el turno: {ex}")

    def ejecutar(self) -> None:
        """
        Loop principal: procesa eventos y dibuja.

        Parámetros:
            Ninguno.

        Retorna:
            None
        """
        corriendo = True
        while corriendo:
            for evento in pygame.event.get():
                if not self.__procesar_evento__(evento):
                    corriendo = False
                    break

            # NUEVO: pasar selección y estado de "puede tirar"; si hay ganador, no puede tirar
            puede_tirar = True
            try:
                puede_tirar = (self.__ganador__ is None) and (not self.__hay_movimientos__())
            except Exception:
                puede_tirar = (self.__ganador__ is None)
            self.__render__.dibujar(
                self.__geo__,
                self.__estado__,
                self.__indice_hover__,
                self.__btn_tirar__,
                self.__seleccion_origen__,
                puede_tirar,
                self.__ganador__,  # NUEVO: ganador para overlay
            )
            # NUEVO: dibujar botón 'Sacar' por encima de todo
            try:
                self.__dibujar_boton_pasar_overlay__()
                self.__dibujar_boton_sacar_overlay__()
                # Ya dibuja dados también por encima
                self.__dibujar_dados_overlay__()
            except Exception:
                pass
            pygame.display.flip()
            self.__reloj__.tick(self.__fps__)

        pygame.quit()
