"""CLI helpers y compatibilidad para interactuar con el Backgammon en consola."""

from __future__ import annotations

import os
import sys
from typing import Any, Sequence

# Asegurar que el root del proyecto esté en sys.path para poder importar 'core'
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Importar constantes con fallback a strings por si core no las expone
try:
    from core import BLANCO, NEGRO
except ImportError:
    BLANCO, NEGRO = "blanco", "negro"

from core.game import Game  # pylint: disable=wrong-import-position
# Alinear constantes y obtener Board desde core.board
try:
    from core.board import Board, BLANCO as BOARD_BLANCO, NEGRO as BOARD_NEGRO  # pylint: disable=wrong-import-position
    BLANCO, NEGRO = BOARD_BLANCO, BOARD_NEGRO
except ImportError:
    from core.board import Board  # pylint: disable=wrong-import-position

# Helpers de compatibilidad para distintos nombres en Game
def _safe_call_methods(
    obj: Any,
    names: Sequence[str],
    *args,
    default=None,
    **kwargs,
):
    """Invoca en orden los métodos nombrados, devolviendo el primero que funcione."""
    for name in names:
        m = getattr(obj, name, None)
        if callable(m):
            try:
                return m(*args, **kwargs)
            except (AttributeError, TypeError, ValueError, RuntimeError):
                pass
    return default

def _coerce_str(val):
    """Normaliza distintos tipos a string amigable para el CLI."""
    if val is None:
        return None
    if isinstance(val, str):
        s = val
    elif isinstance(val, (list, tuple)) and all(isinstance(x, str) for x in val):
        s = "\n".join(val)
    else:
        s = str(val)
    # Evitar repr por defecto de objetos
    if s.startswith("<") and " object at 0x" in s:
        return None
    return s

# Extras: helpers para acceder al Board real desde Game.board (BoardAdapter)
def _get_raw_board(game):
    """Obtiene el tablero "real" detrás de Game.board o adaptadores."""
    b = getattr(game, "tablero", None) or getattr(game, "board", None)
    if b is None:
        return None
    raw = getattr(b, "_b", None)  # BoardAdapter -> Board
    return raw or b

def _board_snapshot(board):
    """Devuelve un snapshot de puntos en formato estándar para render."""
    snap = _safe_call_methods(board, ("points_snapshot", "obtener_estado_puntos"))
    if snap is not None:
        return snap
    # Fallback muy básico desde __posiciones__
    pos = getattr(board, "__posiciones__", None)
    if isinstance(pos, list) and len(pos) == 24:
        out = []
        for pile in pos:
            if pile:
                out.append({"color": pile[0], "cantidad": len(pile)})
            else:
                out.append({"color": None, "cantidad": 0})
        return out
    return None

def _board_counts(board):
    """Cuenta fichas en barra y borne-off a partir de diferentes APIs."""
    # Devuelve dicts de cuentas para barra y fuera
    barra = None
    fuera = None
    # Métodos
    barra = _safe_call_methods(board, ("bar", "obtener_barra"))
    fuera = _safe_call_methods(board, ("borne_off", "obtener_fuera"))
    # Fallback a alias internos
    barra = barra or getattr(board, "__barra__", None)
    fuera = fuera or getattr(board, "__fichas_fuera__", None)
    # Normalizar a conteos
    def to_counts(d):
        if isinstance(d, dict):
            return {
                "blanco": len(d.get("blanco", [])),
                "negro": len(d.get("negro", [])),
            }
        return None
    barra_counts = to_counts(barra) or {"blanco": 0, "negro": 0}
    fuera_counts = to_counts(fuera) or {"blanco": 0, "negro": 0}
    return barra_counts, fuera_counts

def _board_winner(board) -> Any:
    """Intenta inferir el ganador consultando distintas APIs del tablero."""
    winner = _safe_call_methods(
        board,
        ("ganador", "get_ganador", "winner", "get_winner"),
    )
    if winner:
        return winner
    for color in (BLANCO, NEGRO):
        has_won = _safe_call_methods(
            board,
            ("ha_ganado", "has_won", "is_winner"),
            color,
            default=None,
        )
        if isinstance(has_won, bool):
            if has_won:
                return color
        elif has_won:
            return has_won
    return None

def _fmt_point(point: int, cell):
    """Formatea un punto en forma compacta para impresión."""
    c = cell.get("color")
    n = cell.get("cantidad", 0)
    if not c or n == 0:
        return f"{point:02}:__"
    letter = "W" if str(c).lower().startswith("b") else "B"
    return f"{point:02}:{letter}{n}"

def _point_to_board_index(point: int) -> int:
    """Convierte un punto 1..24 (estándar) a índice interno 0..23."""
    if point < 0:
        return point
    if 1 <= point <= 24:
        return 24 - point
    return point

def _render_board_ascii(snapshot, barra_counts, fuera_counts):
    """Construye representación ASCII del tablero con barras."""
    def idx_from_point(point: int) -> int:
        return 24 - point

    top_points = list(range(13, 25))  # 13..24 izquierda->derecha
    bot_points = list(range(12, 0, -1))  # 12..1 izquierda->derecha

    top = " ".join(_fmt_point(p, snapshot[idx_from_point(p)]) for p in top_points)
    bot = " ".join(_fmt_point(p, snapshot[idx_from_point(p)]) for p in bot_points)
    barra_label = f"Barra W:{barra_counts['blanco']} B:{barra_counts['negro']}"
    off = f"Fuera W:{fuera_counts['blanco']} B:{fuera_counts['negro']}"
    return "\n".join([top, bot, barra_label + " | " + off])

def tablero_compacto_str(game) -> str:
    """Obtiene representación textual compacta del tablero."""
    # Primero, probar métodos directos ya existentes
    val = _safe_call_methods(
        game,
        ("tablero_compacto", "tablero_ascii", "tablero_str", "tablero", "mostrar_tablero"),
    )
    s = _coerce_str(val)
    if s:
        return s
    # Intentar vía Board (adaptador o raw)
    board = _get_raw_board(game)
    if board is not None:
        snap = _board_snapshot(board)
        if snap:
            barra_counts, fuera_counts = _board_counts(board)
            return _render_board_ascii(snap, barra_counts, fuera_counts)
        # Último intento: métodos comunes del objeto board
        for name in (
            "compacto",
            "compact",
            "to_compact",
            "to_compact_str",
            "ascii",
            "to_ascii",
            "render",
            "to_string",
            "mostrar",
            "mostrar_tablero",
            "pretty",
            "dump",
        ):
            m = getattr(board, name, None)
            if callable(m):
                try:
                    s2 = _coerce_str(m())
                    if s2:
                        return s2
                except (AttributeError, TypeError, ValueError, RuntimeError):
                    pass
    return "<tablero no disponible>"

def estado_barras_str(game) -> str:
    """Devuelve estado textual de la barra para cada color."""
    board = _get_raw_board(game)
    if board is not None:
        barra_counts, _ = _board_counts(board)
        return (
            "Barra -> blancas: "
            f"{barra_counts['blanco']} | negras: {barra_counts['negro']}"
        )
    # fallback anterior
    val = _safe_call_methods(game, ("estado_barras", "barras_str", "barras", "bar_state"))
    s = _coerce_str(val)
    return s if s else "<barras no disponibles>"

def estado_fuera_str(game) -> str:
    """Devuelve estado textual de fichas borneadas."""
    board = _get_raw_board(game)
    if board is not None:
        _, fuera_counts = _board_counts(board)
        return (
            "Fuera -> blancas: "
            f"{fuera_counts['blanco']} | negras: {fuera_counts['negro']}"
        )
    # fallback anterior
    val = _safe_call_methods(
        game,
        ("estado_fuera", "fuera_str", "bear_off_str", "fuera", "borne_off_state"),
    )
    s = _coerce_str(val)
    return s if s else "<fuera no disponible>"

# Variantes de calls seguros con distintas firmas
def _safe_call_variants(
    obj: Any,
    names: Sequence[str],
    arg_variants: Sequence[tuple[Sequence[Any], dict[str, Any]]],
    default=None,
):
    """Intenta múltiples combinaciones de argumentos contra los nombres provistos."""
    for name in names:
        m = getattr(obj, name, None)
        if callable(m):
            for args, kwargs in arg_variants:
                try:
                    return m(*args, **kwargs)
                except TypeError:
                    continue
                except (AttributeError, ValueError, RuntimeError):
                    continue
    return default

# Turno: obtener valor y formatear
def turno_val(game):
    """Obtiene el objeto que representa el turno actual."""
    val = _safe_call_methods(
        game,
        (
            "turno",
            "get_turno",
            "turno_actual",
            "jugador_en_turno",
            "current_turn",
            "get_current_turn",
            "current_player",
            "get_current_player",
        ),
    )
    if val is None:
        for attr in (
            "turno",
            "turno_actual",
            "current_turn",
            "current_player",
            "jugador_en_turno",
            "jugador_actual",
        ):
            v = getattr(game, attr, None)
            if v is not None:
                val = v
                break
    return val

def turno_color(game):
    """Normaliza el turno a un string (color o nombre)."""
    t = turno_val(game)
    if t is None:
        return None
    # Si es Player, tomar color si existe
    color = getattr(t, "color", None)
    if color:
        return color
    # Si es string u objeto con nombre
    if isinstance(t, str):
        return t
    nombre = getattr(t, "nombre", None) or getattr(t, "name", None)
    return nombre or str(t)

def turno_str(game):
    """Representación amigable del turno."""
    s = turno_color(game)
    return s if s else "<turno?>"

# Tiradas: leer y formatear
def tiradas_val(game):
    """Obtiene la lista de tiradas disponibles, explorando diferentes APIs."""
    # 1) Métodos en Game
    v = _safe_call_methods(
        game,
        ("movimientos_disponibles", "get_movimientos", "get_moves", "dice_moves"),
    )
    if v is not None:
        return v
    # 2) Atributo dice dentro de Game
    dice = getattr(game, "dice", None)
    if dice is not None:
        rest = _safe_call_methods(dice, ("movimientos_restantes", "get_remaining", "remaining"))
        if rest is not None:
            return rest
    # 3) Atributos alternativos
    for name in ("tiradas", "movimientos", "moves_left", "remaining_moves", "jugadas"):
        v2 = getattr(game, name, None)
        if v2 is not None:
            return v2
    return None

def tiradas_str(game):
    """Representación textual de las tiradas restantes."""
    v = tiradas_val(game)
    return str(v) if v else "-"

# Tirar dados (compat nombres)
def tirar_dados_compat(game):
    """Invoca la acción de tirar dados usando las distintas APIs conocidas."""
    # Usar comenzar_turno si existe (Game moderno)
    res = _safe_call_variants(
        game,
        ("comenzar_turno", "start_turn"),
        [((), {})],
        default=None,
    )
    if isinstance(res, bool):
        return res
    # Fallback a APIs antiguas de "tirar"
    alt = _safe_call_variants(
        game,
        ("tirar_dados", "tirar", "roll_dice", "roll"),
        [((), {})],
        default=None,
    )
    # Si no sabemos, asumir True para no bloquear el flujo
    return bool(alt) if alt is not None else True

# Puede mover (con o sin color)
def puede_mover_compat(game):
    """Determina si el juego reporta movimientos disponibles."""
    # Game actual expone puede_mover() sin args
    res = _safe_call_variants(
        game,
        ("puede_mover", "has_moves", "can_move"),
        [((), {})],
        default=None,
    )
    if res is not None:
        return bool(res)
    # ...fallback anterior con color...
    color = turno_color(game)
    res = _safe_call_variants(
        game,
        ("puede_mover", "hay_movimientos", "has_moves", "can_move"),
        [((color,), {}), ((), {})],
        default=None,
    )
    return bool(res)

# Mover ficha (con o sin color)
def mover_compat(game, origen, destino):
    """Aplica un movimiento usando la API más conveniente disponible."""
    norm_origen = _point_to_board_index(origen)
    norm_destino = _point_to_board_index(destino)
    # Game moderno: realizar_movimiento(origen, destino)
    for args in (
        ((norm_origen, norm_destino), {}),
        ((origen, destino), {}),
    ):
        ok = _safe_call_variants(
            game,
            ("realizar_movimiento",),
            [args],
            default=None,
        )
        if isinstance(ok, bool):
            if ok:
                return True
            continue
        if ok is not None:
            return bool(ok)

    # ...fallback a APIs antiguas...
    color = turno_color(game)
    move_variants = [
        ((color, norm_origen, norm_destino), {}),
        ((color, origen, destino), {}),
        ((norm_origen, norm_destino), {}),
        ((origen, destino), {}),
    ]
    for args in move_variants:
        ok = _safe_call_variants(
            game,
            ("mover", "mover_ficha", "move", "move_piece", "apply_move"),
            [args],
            default=None,
        )
        if isinstance(ok, bool):
            if ok:
                return True
            continue
        if ok is not None:
            return bool(ok)
    return False

# Fin de turno si corresponde / avanzar turno
def fin_turno_compat(game):
    """Intenta finalizar el turno si no quedan dados disponibles."""
    # Si no quedan tiradas, intentar terminar_turno()
    if not tiradas_val(game):
        _safe_call_variants(
            game,
            ("terminar_turno", "end_turn", "next_turn", "pasar_turno"),
            [((), {})],
            default=None,
        )
        return True
    return False

# Nuevo helper: compat para obtener el ganador sin romper si no existe
def ganador_val(game):
    """Obtiene el ganador si el juego lo expone por distintos nombres."""
    board = _get_raw_board(game)
    winner = _board_winner(board) if board is not None else None
    if winner:
        return winner
    winner = _safe_call_methods(
        game,
        ("ganador", "get_ganador", "winner", "get_winner"),
    )
    if winner:
        return winner
    for attr in ("ganador", "winner"):
        v = getattr(game, attr, None)
        if v:
            return v
    ended = _safe_call_methods(
        game,
        ("terminado", "finalizado", "fin", "is_over", "game_over"),
    )
    if ended:
        for attr in (
            "ganador",
            "winner",
            "ganador_color",
            "winner_color",
            "victor",
            "victoria",
        ):
            v = getattr(game, attr, None)
            if v:
                return v
    return None

# NUEVO: interacción para mover inmediatamente tras tirar
def _interactuar_movimientos(game):
    """Bucle interactivo para consumir movimientos restantes."""
    if not tiradas_val(game) or not puede_mover_compat(game):
        return
    print(
        "Ingresá los movimientos como: <origen> <destino> (origen=-1 para barra). "
        "Escribí 'fin' para terminar."
    )
    while tiradas_val(game):
        if not puede_mover_compat(game):
            print("Sin movimientos. Se pasa el turno.")
            fin_turno_compat(game)
            break
        try:
            linea = input(f"[{turno_str(game)} mover] ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not linea:
            continue
        if linea.lower() in ("fin", "pass", "pasar"):
            fin_turno_compat(game)
            print(f"Turno de {turno_str(game)}.")
            break
        parts = linea.split()
        if len(parts) != 2:
            print("Uso: <origen> <destino> (origen=-1 para barra)")
            continue
        try:
            origen = int(parts[0])
            destino = int(parts[1])
        except ValueError:
            print("Origen y destino deben ser enteros.")
            continue

        if mover_compat(game, origen, destino):
            print("OK.")
            print(tablero_compacto_str(game))
            if fin_turno_compat(game):
                print(f"Turno de {turno_str(game)}.")
                break
            print(f"Tiradas restantes: {tiradas_str(game)}")
        else:
            print("Movimiento inválido (bloqueo o no coincide con dados).")

def main() -> int:
    """Loop principal del CLI interactivo."""
    # pylint: disable=too-many-branches,too-many-statements
    # Asegurar orden correcto: inicializar Game con un Board real
    # blanco = Player(nombre="Blancas", color=BLANCO)
    # negro = Player(nombre="Negras", color=NEGRO)
    # game = Game(blanco, negro)
    board = Board()
    game = Game(board=board, jugador_inicial=BLANCO)

    print("Backgammon CLI")
    print(f"Colores: {BLANCO} vs {NEGRO}")
    print(
        "Comandos: tablero, barra, fuera, tirar, mover, mover_barra, "
        "turno, pasar, reset, salir"
    )
    # Mostrar tablero inicial para validar visualmente
    print(tablero_compacto_str(game))

    while True:
        ganador = ganador_val(game)
        if ganador:
            print(f"¡Ganó {ganador}!")
            return 0

        try:
            linea = input(f"[{turno_str(game)}] ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not linea:
            continue

        parts = linea.split()
        cmd, *args = parts
        cmd = cmd.lower()

        if cmd in ("salir", "exit", "quit"):
            break

        if cmd == "tablero":
            print(tablero_compacto_str(game))
        elif cmd == "barra":
            print(estado_barras_str(game))
        elif cmd == "fuera":
            print(estado_fuera_str(game))
        elif cmd == "turno":
            print(f"Turno: {turno_str(game)} | Tiradas: {tiradas_str(game)}")
        elif cmd == "reset":
            # Reiniciar tablero y dados, y volver a BLANCO
            raw_board = _get_raw_board(game)
            _safe_call_methods(
                raw_board or getattr(game, "board", None),
                ("inicializar_posiciones", "reset_to_start", "reset"),
            )
            _safe_call_methods(game, ("reset", "reiniciar"))
            _safe_call_methods(game.dice, ("reiniciar_turno",))
            try:
                game.jugador_actual = BLANCO
            except AttributeError:
                pass
            print("Partida reiniciada.")
            print(tablero_compacto_str(game))
        elif cmd == "tirar":
            if tiradas_val(game):
                print(f"Ya hay tiradas: {tiradas_str(game)}")
            else:
                pudo = tirar_dados_compat(game)
                print(f"Tiradas: {tiradas_str(game)}")
                if not puede_mover_compat(game):
                    print("Sin movimientos. Se pasa el turno.")
                    fin_turno_compat(game)
                elif not pudo:
                    # comenzar_turno devolvió False => pasó el turno
                    print(f"Turno de {turno_str(game)}.")
                else:
                    # NUEVO: pedir inmediatamente el movimiento
                    _interactuar_movimientos(game)
        elif cmd == "mover":
            if len(args) != 2:
                print("Uso: mover <origen> <destino> (origen=-1 para barra)")
                continue
            try:
                origen = int(args[0])
                destino = int(args[1])
            except ValueError:
                print("Origen y destino deben ser enteros.")
                continue
            if not tiradas_val(game):
                print("Primero tirá los dados con 'tirar'.")
                continue
            if mover_compat(game, origen, destino):
                print("OK.")
                print(tablero_compacto_str(game))
                if fin_turno_compat(game):
                    print(f"Turno de {turno_str(game)}.")
                else:
                    print(f"Tiradas restantes: {tiradas_str(game)}")
            else:
                print("Movimiento inválido (bloqueo o no coincide con dados).")
        elif cmd == "mover_barra":
            if len(args) != 1:
                print("Uso: mover_barra <destino>")
                continue
            try:
                destino = int(args[0])
            except ValueError:
                print("Destino debe ser entero.")
                continue
            if not tiradas_val(game):
                print("Primero tirá los dados con 'tirar'.")
                continue
            if mover_compat(game, -1, destino):
                print("OK.")
                print(tablero_compacto_str(game))
                if fin_turno_compat(game):
                    print(f"Turno de {turno_str(game)}.")
                else:
                    print(f"Tiradas restantes: {tiradas_str(game)}")
            else:
                print("No se pudo reingresar (bloqueo o no coincide con dados).")
        elif cmd == "pasar":
            _safe_call_variants(
                game,
                ("saltear_turno", "terminar_turno", "end_turn", "next_turn", "pasar_turno"),
                [((), {})],
                default=None,
            )
            print(f"Turno de {turno_str(game)}.")
        else:
            print("Comando desconocido.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
