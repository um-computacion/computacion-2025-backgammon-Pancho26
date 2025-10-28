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
        self.__layout__ = geometry.MotorDisposicion(margen=20, fraccion_barra=0.06)
        self.__geo__: geometry.GeometriaTablero = self.__layout__.construir(
            ancho, alto, self.__tema__.__punta_a__, self.__tema__.__punta_b__, self.__tema__.__barra__
        )
        self.__deteccion__ = DeteccionPuntas(self.__geo__.__triangulos__)
        self.__render__ = RenderizadorTablero(self.__pantalla__, self.__fuente__, self.__tema__)
        self.__estado__ = estado  # se inyecta desde la capa de juego
        self.__indice_hover__: Optional[int] = None
        # NUEVO: rect del botón "Tirar"
        self.__btn_tirar__: pygame.Rect = self.__calc_rect_boton_tirar__()
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
            nuevo_ancho, nuevo_alto, self.__tema__.__punta_a__, self.__tema__.__punta_b__, self.__tema__.__barra__
        )
        self.__deteccion__.actualizar_triangulos(self.__geo__.__triangulos__)
        # NUEVO: actualizar rect del botón al redimensionar
        self.__btn_tirar__ = self.__calc_rect_boton_tirar__()

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
        # NUEVO: tirar dados con 'R'
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            self.__tirar_dados__()
        if evento.type == pygame.VIDEORESIZE:
            self.__redimensionar__(evento.w, evento.h)
        elif evento.type == pygame.MOUSEMOTION:
            self.__indice_hover__ = self.__deteccion__.buscar_indice_punta(evento.pos)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
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
            pygame.display.flip()
            self.__reloj__.tick(self.__fps__)

        pygame.quit()