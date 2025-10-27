"""
Punto de entrada de la app. Permite ejecutar en modo CLI o Pygame.
"""

from dataclasses import dataclass
from typing import Optional
import argparse

from juego.state import EstadoJuego


@dataclass
class CLIBackgammon:
    """
    CLI mínima para interactuar con EstadoJuego.

    Atributos:
        __estado__ (EstadoJuego): Estado del juego.
        __activo__ (bool): Control del loop.
    """
    __estado__: EstadoJuego
    __activo__: bool = True

    def __ayuda__(self) -> None:
        """
        Muestra comandos disponibles.
        """
        print(
            "Comandos:\n"
            "  ayuda                         Muestra esta ayuda\n"
            "  mostrar                       Muestra tablero resumido\n"
            "  estado                        Muestra barras, fuera y turno\n"
            "  reset                         Posición inicial\n"
            "  dados D1 D2                   Setea dados (1..6). Dobles=4 movs\n"
            "  mover DESDE PASOS             Mueve una ficha (usa un dado)\n"
            "  reingresar PASOS              Reingresa desde barra (usa un dado)\n"
            "  turno                         Cambia el turno (limpia dados)\n"
            "  salir                         Termina\n"
        )

    def __mostrar__(self) -> None:
        """
        Muestra conteos simples por punto (B=blancas, N=negras).
        """
        e = self.__estado__
        filas = []
        for p in range(24, 12, -1):
            b, n = e.__blancas__[p], e.__negras__[p]
            filas.append(f"{p:>2}:B{b:>2}/N{n:<2}")
        print("Cuadrante superior (24→13):")
        print("  " + "  ".join(filas))

        filas = []
        for p in range(12, 0, -1):
            b, n = e.__blancas__[p], e.__negras__[p]
            filas.append(f"{p:>2}:B{b:>2}/N{n:<2}")
        print("Cuadrante inferior (12→1):")
        print("  " + "  ".join(filas))

    def __mostrar_estado__(self) -> None:
        """
        Muestra barras, borne-off y turno/dados.
        """
        e = self.__estado__
        print(
            f"Turno: {e.__turno__}  Dados: {e.__dados__}  Pendientes: {e.__movimientos_pendientes__}\n"
            f"Barra B/N: {e.__bar_blancas__}/{e.__bar_negras__}  Fuera B/N: {e.__fuera_blancas__}/{e.__fuera_negras__}"
        )

    def ejecutar(self) -> None:
        """
        Loop principal de CLI.
        """
        print("Backgammon (CLI). Escriba 'ayuda' para ver comandos.")
        while self.__activo__:
            try:
                linea = input("bg> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not linea:
                continue
            partes = linea.split()
            cmd = partes[0].lower()
            args = partes[1:]

            try:
                if cmd == "ayuda":
                    self.__ayuda__()
                elif cmd == "mostrar":
                    self.__mostrar__()
                elif cmd == "estado":
                    self.__mostrar_estado__()
                elif cmd == "reset":
                    self.__estado__.restablecer_inicio()
                    print("Posición inicial establecida.")
                elif cmd == "dados":
                    if len(args) != 2:
                        print("Uso: dados D1 D2")
                        continue
                    d1, d2 = int(args[0]), int(args[1])
                    self.__estado__.set_dados(d1, d2)
                    print(f"Dados seteados: {d1}, {d2} → {self.__estado__.__movimientos_pendientes__}")
                elif cmd == "mover":
                    if len(args) != 2:
                        print("Uso: mover DESDE PASOS")
                        continue
                    desde, pasos = int(args[0]), int(args[1])
                    if not self.__estado__.puede_mover(desde, pasos):
                        print("Movimiento inválido.")
                        continue
                    self.__estado__.mover(desde, pasos)
                    print("Movimiento aplicado.")
                elif cmd == "reingresar":
                    if len(args) != 1:
                        print("Uso: reingresar PASOS")
                        continue
                    pasos = int(args[0])
                    if not self.__estado__.puede_reingresar(pasos):
                        print("Reingreso inválido.")
                        continue
                    self.__estado__.reingresar(pasos)
                    print("Reingreso aplicado.")
                elif cmd == "turno":
                    self.__estado__.cambiar_turno()
                    print(f"Turno cambiado a {self.__estado__.__turno__}.")
                elif cmd == "salir":
                    self.__activo__ = False
                else:
                    print("Comando no reconocido. Use 'ayuda'.")
            except ValueError as ex:
                print(f"Error: {ex}")


class Aplicacion:
    """
    Orquestador de modos de ejecución.

    Atributos:
        __modo__ (str): 'cli' o 'pygame'.
        __ancho__, __alto__, __fps__ (int): Parámetros de ventana Pygame.
        __estado__ (EstadoJuego): Estado compartido.
    """

    def __init__(self, modo: str, ancho: int, alto: int, fps: int) -> None:
        """
        Inicializa la aplicación.
        """
        self.__modo__ = modo
        self.__ancho__ = ancho
        self.__alto__ = alto
        self.__fps__ = fps
        self.__estado__ = EstadoJuego()
        self.__estado__.restablecer_inicio()

    def ejecutar(self) -> None:
        """
        Ejecuta en el modo seleccionado.
        """
        if self.__modo__ == "pygame":
            # Import diferido para no requerir pygame en modo CLI.
            from ui.controller import ControladorUI
            ui = ControladorUI(
                ancho=self.__ancho__,
                alto=self.__alto__,
                estado=self.__estado__,
                fps=self.__fps__,
                titulo="Backgammon - Pygame",
            )
            ui.ejecutar()
        else:
            cli = CLIBackgammon(self.__estado__)
            cli.ejecutar()


def main(argv: Optional[list] = None) -> None:
    """
    Parser de argumentos y arranque.
    """
    parser = argparse.ArgumentParser(description="Backgammon - App")
    parser.add_argument("--modo", choices=["cli", "pygame"], default="cli", help="Modo de ejecución")
    parser.add_argument("--ancho", type=int, default=1000, help="Ancho de ventana (pygame)")
    parser.add_argument("--alto", type=int, default=700, help="Alto de ventana (pygame)")
    parser.add_argument("--fps", type=int, default=60, help="FPS (pygame)")
    args = parser.parse_args(argv)

    app = Aplicacion(modo=args.modo, ancho=args.ancho, alto=args.alto, fps=args.fps)
    app.ejecutar()

if __name__ == "__main__":
    main()