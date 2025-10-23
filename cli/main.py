import os, sys
# Asegurar que el root del proyecto esté en sys.path para poder importar 'core'
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
	 sys.path.insert(0, _PROJECT_ROOT)

# Importar constantes con fallback a strings por si core no las expone
try:
    from core import BLANCO, NEGRO
except Exception:
    BLANCO, NEGRO = "blanco", "negro"

from core.player import Player
from core.game import Game
# Alinear constantes y obtener Board desde core.board
try:
    from core.board import Board, BLANCO as BOARD_BLANCO, NEGRO as BOARD_NEGRO
    BLANCO, NEGRO = BOARD_BLANCO, BOARD_NEGRO
except Exception:
    from core.board import Board

# Helpers de compatibilidad para distintos nombres en Game
def _safe_call_methods(obj, names, *args, default=None, **kwargs):
    for name in names:
        m = getattr(obj, name, None)
        if callable(m):
            try:
                return m(*args, **kwargs)
            except Exception:
                pass
    return default

def _coerce_str(val):
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
    b = getattr(game, "tablero", None) or getattr(game, "board", None)
    if b is None:
        return None
    raw = getattr(b, "_b", None)  # BoardAdapter -> Board
    return raw or b

def _board_snapshot(board):
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
    return to_counts(barra) or {"blanco": 0, "negro": 0}, to_counts(fuera) or {"blanco": 0, "negro": 0}

def _fmt_point(idx, cell):
    c = cell.get("color")
    n = cell.get("cantidad", 0)
    if not c or n == 0:
        return f"{idx:02}:__"
    letter = "W" if str(c).lower().startswith("b") else "B"
    return f"{idx:02}:{letter}{n}"

def _render_board_ascii(snapshot, barra_counts, fuera_counts):
    # Top: 23..12, Bottom: 0..11
    top = " ".join(_fmt_point(i, snapshot[i]) for i in range(23, 11, -1))
    bot = " ".join(_fmt_point(i, snapshot[i]) for i in range(0, 12))
    bar = f"Barra W:{barra_counts['blanco']} B:{barra_counts['negro']}"
    off = f"Fuera W:{fuera_counts['blanco']} B:{fuera_counts['negro']}"
    return "\n".join([top, bot, bar + " | " + off])

def tablero_compacto_str(game) -> str:
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
        for name in ("compacto", "compact", "to_compact", "to_compact_str", "ascii", "to_ascii", "render", "to_string", "mostrar", "mostrar_tablero", "pretty", "dump"):
            m = getattr(board, name, None)
            if callable(m):
                try:
                    s2 = _coerce_str(m())
                    if s2:
                        return s2
                except Exception:
                    pass
    return "<tablero no disponible>"

def estado_barras_str(game) -> str:
    board = _get_raw_board(game)
    if board is not None:
        barra_counts, _ = _board_counts(board)
        return f"Barra -> blancas: {barra_counts['blanco']} | negras: {barra_counts['negro']}"
    # fallback anterior
    val = _safe_call_methods(game, ("estado_barras", "barras_str", "barras", "bar_state"))
    s = _coerce_str(val)
    return s if s else "<barras no disponibles>"

def estado_fuera_str(game) -> str:
    board = _get_raw_board(game)
    if board is not None:
        _, fuera_counts = _board_counts(board)
        return f"Fuera -> blancas: {fuera_counts['blanco']} | negras: {fuera_counts['negro']}"
    # fallback anterior
    val = _safe_call_methods(game, ("estado_fuera", "fuera_str", "bear_off_str", "fuera", "borne_off_state"))
    s = _coerce_str(val)
    return s if s else "<fuera no disponible>"

# Variantes de calls seguros con distintas firmas
def _safe_call_variants(obj, names, arg_variants, default=None):
    for name in names:
        m = getattr(obj, name, None)
        if callable(m):
            for args, kwargs in arg_variants:
                try:
                    return m(*args, **kwargs)
                except TypeError:
                    continue
                except Exception:
                    continue
    return default

# Turno: obtener valor y formatear
def turno_val(game):
    val = _safe_call_methods(game, ("turno", "get_turno", "turno_actual", "jugador_en_turno", "current_turn", "get_current_turn", "current_player", "get_current_player"))
    if val is None:
        for attr in ("turno", "turno_actual", "current_turn", "current_player", "jugador_en_turno", "jugador_actual"):
            v = getattr(game, attr, None)
            if v is not None:
                val = v
                break
    return val

def turno_color(game):
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
    s = turno_color(game)
    return s if s else "<turno?>"

# Tiradas: leer y formatear
def tiradas_val(game):
    # 1) Métodos en Game
    v = _safe_call_methods(game, ("movimientos_disponibles", "get_movimientos", "get_moves", "dice_moves"))
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
    v = tiradas_val(game)
    return str(v) if v else "-"

# Tirar dados (compat nombres)
def tirar_dados_compat(game):
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
    # Game actual expone puede_mover() sin args
    res = _safe_call_variants(game, ("puede_mover", "has_moves", "can_move"), [((), {})], default=None)
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
    # Game moderno: realizar_movimiento(origen, destino)
    ok = _safe_call_variants(
        game,
        ("realizar_movimiento",),
        [((origen, destino), {})],
        default=None,
    )
    if isinstance(ok, bool):
        return ok
    # ...fallback a APIs antiguas...
    color = turno_color(game)
    return bool(_safe_call_variants(
        game,
        ("mover", "mover_ficha", "move", "move_piece", "apply_move"),
        [((color, origen, destino), {}), ((origen, destino), {})],
        default=False,
    ))

# Fin de turno si corresponde / avanzar turno
def fin_turno_compat(game):
    # Si no quedan tiradas, intentar terminar_turno()
    if not tiradas_val(game):
        done = _safe_call_variants(
            game,
            ("terminar_turno", "end_turn", "next_turn", "pasar_turno"),
            [((), {})],
            default=None,
        )
        return True if done is None or isinstance(done, bool) else True
    return False

# Nuevo helper: compat para obtener el ganador sin romper si no existe
def ganador_val(game):
    val = _safe_call_methods(game, ("ganador", "get_ganador", "winner", "get_winner"))
    if val:
        return val
    for attr in ("ganador", "winner"):
        v = getattr(game, attr, None)
        if v:
            return v
    ended = _safe_call_methods(game, ("terminado", "finalizado", "fin", "is_over", "game_over"))
    if ended:
        for attr in ("ganador", "winner", "ganador_color", "winner_color", "victor", "victoria"):
            v = getattr(game, attr, None)
            if v:
                return v
    return None

# NUEVO: interacción para mover inmediatamente tras tirar
def _interactuar_movimientos(game):
    if not tiradas_val(game) or not puede_mover_compat(game):
        return
    print("Ingresá los movimientos como: <origen> <destino> (origen=-1 para barra). Escribí 'fin' para terminar.")
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
            origen = int(parts[0]); destino = int(parts[1])
        except Exception:
            print("Origen y destino deben ser enteros.")
            continue

        if mover_compat(game, origen, destino):
            print("OK.")
            print(tablero_compacto_str(game))
            if fin_turno_compat(game):
                print(f"Turno de {turno_str(game)}.")
                break
            else:
                print(f"Tiradas restantes: {tiradas_str(game)}")
        else:
            print("Movimiento inválido (bloqueo o no coincide con dados).")

def main() -> int:
    # Asegurar orden correcto: inicializar Game con un Board real
    # blanco = Player(nombre="Blancas", color=BLANCO)
    # negro = Player(nombre="Negras", color=NEGRO)
    # game = Game(blanco, negro)
    board = Board()
    game = Game(board=board, jugador_inicial=BLANCO)

    print("Backgammon CLI")
    print("Comandos: tablero, barra, fuera, tirar, mover, mover_barra, turno, pasar, reset, salir")
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
        elif cmd == "tablero":
            print(tablero_compacto_str(game))
        elif cmd == "barra":
            print(estado_barras_str(game))
        elif cmd == "fuera":
            print(estado_fuera_str(game))
        elif cmd == "turno":
            print(f"Turno: {turno_str(game)} | Tiradas: {tiradas_str(game)}")
        elif cmd == "reset":
            # Reiniciar tablero y dados, y volver a BLANCO
            _safe_call_methods(game.board, ("inicializar_posiciones", "reset_to_start", "reset"))
            _safe_call_methods(game.dice, ("reiniciar_turno",))
            try:
                game.jugador_actual = BLANCO
            except Exception:
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
                origen = int(args[0]); destino = int(args[1])
            except Exception:
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
            except Exception:
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
            if tiradas_val(game) and puede_mover_compat(game):
                print("Aún hay movimientos posibles; no se puede pasar.")
            else:
                fin_turno_compat(game)
                print(f"Turno de {turno_str(game)}.")
        else:
            print("Comando desconocido.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())