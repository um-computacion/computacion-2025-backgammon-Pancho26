"""
Punto de entrada de la app. Permite ejecutar en modo CLI o Pygame.
"""

from typing import Optional
import argparse
import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from cli.state import EstadoJuego


class Aplicacion:
    """
    Orquestador de ejecución (solo Pygame).
    """

    def __init__(
        self,
        ancho: int,
        alto: int,
        fps: int,
        dice_on_top: bool = True,
        dice_position: str = "top",
        dice_y_offset: int = 16,
    ) -> None:
        """
        Inicializa la aplicación.
        """
        self.__ancho__ = ancho
        self.__alto__ = alto
        self.__fps__ = fps
        # Preferencias de render de dados
        self.__dice_on_top__ = dice_on_top
        self.__dice_position__ = dice_position
        self.__dice_y_offset__ = dice_y_offset

        self.__estado__ = EstadoJuego()

        # Exportar preferencias de dados a estado/env para que la UI las use
        setattr(self.__estado__, "dice_draw_on_top", dice_on_top)
        setattr(self.__estado__, "dice_position", dice_position)  # "top" | "bottom"
        setattr(self.__estado__, "dice_y_offset", dice_y_offset)  # px
        os.environ["BACKGAMMON_DICE_DRAW_ON_TOP"] = "1" if dice_on_top else "0"
        os.environ["BACKGAMMON_DICE_POSITION"] = dice_position
        os.environ["BACKGAMMON_DICE_Y_OFFSET"] = str(dice_y_offset)

        self.__estado__.restablecer_inicio()

    def ejecutar(self) -> None:
        """
        Ejecuta en el modo seleccionado.
        """
        from ui.controller import ControladorUI
        ui = ControladorUI(
            ancho=self.__ancho__,
            alto=self.__alto__,
            estado=self.__estado__,
            fps=self.__fps__,
            titulo="Backgammon - Pygame",
        )
        ui.ejecutar()


def main(argv: Optional[list] = None) -> None:
    """
    Parser de argumentos y arranque.
    """
    parser = argparse.ArgumentParser(description="Backgammon - App (Pygame)")
    parser.add_argument("--ancho", type=int, default=1000, help="Ancho de ventana (pygame)")
    parser.add_argument("--alto", type=int, default=700, help="Alto de ventana (pygame)")
    parser.add_argument("--fps", type=int, default=60, help="FPS (pygame)")
    # Control de render de dados para evitar que las fichas superiores los tapen
    parser.add_argument(
        "--dados-encima",
        dest="dice_on_top",
        action="store_true",
        default=True,
        help="Dibuja los dados por encima de las fichas (z-order)",
    )
    parser.add_argument(
        "--dados-debajo",
        dest="dice_on_top",
        action="store_false",
        help="Dibuja los dados por debajo de las fichas",
    )
    parser.add_argument(
        "--dados-posicion",
        choices=["top", "bottom"],
        default="top",
        help="Posición preferida de los dados en el tablero",
    )
    parser.add_argument(
        "--dados-offset-y",
        type=int,
        default=16,
        help="Desplazamiento vertical adicional para los dados (px)",
    )
    args = parser.parse_args(argv)

    app = Aplicacion(
        ancho=args.ancho,
        alto=args.alto,
        fps=args.fps,
        dice_on_top=args.dice_on_top,
        dice_position=args.dados_posicion if hasattr(args, "dados_posicion") else args.dice_position if hasattr(args, "dice_position") else "top",  # compat
        dice_y_offset=args.dados_offset_y if hasattr(args, "dados_offset_y") else args.dice_offset_y if hasattr(args, "dice_offset_y") else 16,
    )
    app.ejecutar()

if __name__ == "__main__":
    main()
