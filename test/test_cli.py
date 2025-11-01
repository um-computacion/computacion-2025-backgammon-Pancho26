import os
import sys
import types
import importlib
import importlib.util
from pathlib import Path

def _install_dummy_ui(monkeypatch, captured):
    """
    Registra un módulo ui.controller falso en sys.modules con una clase ControladorUI
    que captura los argumentos y no abre ninguna ventana.
    """
    mod = types.ModuleType("ui.controller")

    class DummyControladorUI:
        def __init__(self, ancho, alto, estado, fps, titulo):
            captured["ancho"] = ancho
            captured["alto"] = alto
            captured["fps"] = fps
            captured["titulo"] = titulo
            captured["estado"] = estado

        def ejecutar(self):
            captured["ejecuto"] = True

    mod.ControladorUI = DummyControladorUI
    monkeypatch.setitem(importlib.sys.modules, "ui.controller", mod)


def test_main_defaults_set_state_and_env(monkeypatch):
    from cli import app as cli_app
    captured = {}
    _install_dummy_ui(monkeypatch, captured)
    # Asegurar entorno limpio
    monkeypatch.delenv("BACKGAMMON_AUTO_SKIP_NO_MOVES", raising=False)

    # Ejecuta con valores por defecto
    cli_app.main(argv=[])

    # Se debe haber llamado a la UI con los defaults
    assert captured["ancho"] == 1000
    assert captured["alto"] == 700
    assert captured["fps"] == 60
    assert captured["titulo"]  # no validamos el texto exacto

    # Lógica: auto_skip por defecto activado en estado y env
    estado = captured["estado"]
    assert getattr(estado, "auto_skip_no_moves", None) is True
    assert os.environ.get("BACKGAMMON_AUTO_SKIP_NO_MOVES") == "1"


def test_main_flags_override_and_env_off(monkeypatch):
    from cli import app as cli_app
    captured = {}
    _install_dummy_ui(monkeypatch, captured)
    monkeypatch.delenv("BACKGAMMON_AUTO_SKIP_NO_MOVES", raising=False)

    # Override de flags
    cli_app.main(argv=[
        "--no-saltear-sin-movimientos",
        "--ancho", "800",
        "--alto", "600",
        "--fps", "30",
    ])

    # Se debe haber llamado a la UI con los argumentos pasados
    assert captured["ancho"] == 800
    assert captured["alto"] == 600
    assert captured["fps"] == 30

    # Lógica: auto_skip desactivado en estado y env
    estado = captured["estado"]
    assert getattr(estado, "auto_skip_no_moves", None) is False
    assert os.environ.get("BACKGAMMON_AUTO_SKIP_NO_MOVES") == "0"


def test_safe_helpers_cover_variants():
    from cli import main as cli_main

    class WithMethods:
        def fail(self):
            raise ValueError("boom")

        def ok(self, extra=None):
            return f"ok-{extra}"

    obj = WithMethods()
    assert cli_main._safe_call_methods(obj, ("missing", "fail", "ok"), "x") == "ok-x"
    assert cli_main._safe_call_methods(obj, ("missing",), default="fallback") == "fallback"

    class Dummy:
        def __str__(self):
            return "<Dummy object at 0x123>"

    assert cli_main._coerce_str(None) is None
    assert cli_main._coerce_str("direct") == "direct"
    assert cli_main._coerce_str(["a", "b"]) == "a\nb"
    assert cli_main._coerce_str(Dummy()) is None


def test_board_helpers_render_snapshot():
    from cli import main as cli_main

    class DummyBoard:
        def __init__(self):
            self.calls = []
            self.__posiciones__ = [["blanco"] * 2 if i % 3 == 0 else [] for i in range(24)]

        def points_snapshot(self):
            self.calls.append("points_snapshot")
            return [{"color": "blanco", "cantidad": 2} for _ in range(24)]

        def bar(self):
            return {"blanco": [1, 2], "negro": [3]}

        def borne_off(self):
            return {"blanco": [1], "negro": []}

    board = DummyBoard()
    snapshot = cli_main._board_snapshot(board)
    assert snapshot and snapshot[0]["cantidad"] == 2
    barra, fuera = cli_main._board_counts(board)
    assert barra == {"blanco": 2, "negro": 1}
    assert fuera == {"blanco": 1, "negro": 0}
    ascii_board = cli_main._render_board_ascii(snapshot, barra, fuera)
    assert "Barra" in ascii_board

    class WithoutSnapshot(DummyBoard):
        def points_snapshot(self):
            return None

    board2 = WithoutSnapshot()
    snapshot2 = cli_main._board_snapshot(board2)
    assert snapshot2[0]["color"] == "blanco"


def test_tablero_and_estado_strings_cover_fallbacks():
    from cli import main as cli_main

    class MinimalBoard:
        def __init__(self):
            self.__posiciones__ = [[] for _ in range(24)]

    class MinimalGame:
        def __init__(self, board):
            self.board = board
            self.tablero = board  # Compatibility attribute
            self.dice = types.SimpleNamespace()

        def tablero_compacto(self):
            return ["linea1", "linea2"]

        def estado_barras(self):
            return "barras!"

        def estado_fuera(self):
            return ["fuera1", "fuera2"]

    game = MinimalGame(MinimalBoard())
    game.board = None
    game.tablero = None
    assert "linea1" in cli_main.tablero_compacto_str(game)
    assert cli_main.estado_barras_str(game) == "barras!"
    assert "fuera1" in cli_main.estado_fuera_str(game)

    class SilentGame(MinimalGame):
        def tablero_compacto(self):
            raise RuntimeError("broken")

        def estado_barras(self):
            raise RuntimeError("broken")

        def estado_fuera(self):
            raise RuntimeError("broken")

    board = MinimalBoard()
    silent_game = SilentGame(board)
    board.__posiciones__[0] = ["blanco"]
    assert "<tablero no disponible>" not in cli_main.tablero_compacto_str(silent_game)
    barras = cli_main.estado_barras_str(silent_game)
    fuera = cli_main.estado_fuera_str(silent_game)
    assert barras.startswith("Barra ->")
    assert fuera.startswith("Fuera ->")


def test_tablero_compacto_usa_metodos_del_tablero():
    from cli import main as cli_main

    class BoardWithMethod:
        def points_snapshot(self):
            return None

        def compacto(self):
            return "compact-board"

    board = BoardWithMethod()
    game = types.SimpleNamespace(board=board, tablero=board)
    assert cli_main.tablero_compacto_str(game) == "compact-board"


def test_safe_call_variants_gestiona_excepciones():
    from cli import main as cli_main

    class CallableSet:
        def primero(self, *_, **__):
            raise TypeError("boom")

        def segundo(self, *_, **__):
            raise RuntimeError("fail")

        def tercero(self, *args, **kwargs):
            return ("ok", args, kwargs)

    res = cli_main._safe_call_variants(
        CallableSet(),
        ("primero", "segundo", "tercero"),
        [((), {}), ((1,), {})],
        default="fallback",
    )
    assert res[0] == "ok"


def test_turno_val_y_color_por_atributos():
    from cli import main as cli_main

    class AttrGame:
        def __init__(self):
            self.jugador_actual = types.SimpleNamespace(nombre="Nom")

    attr_game = AttrGame()
    assert cli_main.turno_val(attr_game).nombre == "Nom"
    assert cli_main.turno_color(attr_game) == "Nom"
    assert cli_main.turno_str(attr_game) == "Nom"

    class EmptyGame:
        pass

    assert cli_main.turno_color(EmptyGame()) is None


def test_tiradas_val_por_atributos_y_fallbacks():
    from cli import main as cli_main

    class MovesGame:
        def __init__(self):
            self.dice = None
            self.tiradas = None
            self.moves_left = [1, 2]

    moves_game = MovesGame()
    assert cli_main.tiradas_val(moves_game) == [1, 2]
    assert cli_main.tiradas_str(moves_game) == "[1, 2]"


def test_tirar_y_mover_compatibles_fallbacks():
    from cli import main as cli_main

    class CompatGame:
        def __init__(self):
            self.jugador_actual = "blanco"
            self._moves = [("blanco", 1, 2)]

        def comenzar_turno(self):
            return None

        def tirar_dados(self):
            return 0

        def puede_mover(self, color):
            return color == "blanco"

        def mover(self, color, origen, destino):
            return (color, origen, destino) in self._moves

    game = CompatGame()
    assert cli_main.tirar_dados_compat(game) is False
    assert cli_main.puede_mover_compat(game) is True
    assert cli_main.mover_compat(game, 1, 2) is True

def test_turno_and_tiradas_helpers(monkeypatch):
    from cli import main as cli_main

    class DummyDice:
        def __init__(self):
            self.remaining = ["a", "b"]

        def movimientos_restantes(self):
            return self.remaining

    class Player:
        def __init__(self, color):
            self.color = color
            self.nombre = f"Jugador {color}"

    class DummyGame:
        def __init__(self):
            self.turno = Player(cli_main.BLANCO)
            self.dice = DummyDice()
            self.movimientos = ["x"]
            self.tiradas = None

        def turno_actual(self):
            return self.turno

        def get_movimientos(self):
            return self.movimientos

        def puede_mover(self, *_):
            return False

        def tirar_dados(self):
            return True

        def mover(self, *_):
            return True

        def terminar_turno(self):
            return True

    game = DummyGame()
    assert cli_main.turno_val(game)
    assert cli_main.turno_color(game) == cli_main.BLANCO
    assert cli_main.turno_str(game) == cli_main.BLANCO
    assert cli_main.tiradas_val(game) == game.movimientos
    game.movimientos = None
    assert cli_main.tiradas_val(game) == game.dice.movimientos_restantes()
    assert cli_main.tiradas_str(game) != "-"
    assert cli_main.tirar_dados_compat(game) is True
    assert cli_main.puede_mover_compat(game) is False
    assert cli_main.mover_compat(game, 1, 2) is True
    game.dice.remaining = []
    assert cli_main.fin_turno_compat(game) is True


def test_ganador_val_variants():
    from cli import main as cli_main

    class MethodGame:
        def ganador(self):
            return "blanco"

    assert cli_main.ganador_val(MethodGame()) == "blanco"

    class DummyGame:
        def __init__(self):
            self.ganador = None
            self.winner_color = None
            self._called = False

        def terminado(self):
            self._called = True
            return True

    game = DummyGame()
    assert cli_main.ganador_val(game) is None
    game.winner_color = "blanco"
    assert cli_main.ganador_val(game) == "blanco"
    assert game._called is True


def test_interactive_main_flow(monkeypatch, capsys):
    from cli import main as cli_main

    class TestBoard:
        def __init__(self):
            self.reset_calls = 0
            self.__posiciones__ = [{"color": None, "cantidad": 0} for _ in range(24)]

        def points_snapshot(self):
            snap = []
            for i in range(24):
                if i % 2 == 0:
                    snap.append({"color": "blanco", "cantidad": 2})
                else:
                    snap.append({"color": "negro", "cantidad": 1})
            return snap

        def bar(self):
            return {"blanco": [1], "negro": []}

        def borne_off(self):
            return {"blanco": [], "negro": ["x"]}

        def inicializar_posiciones(self):
            self.reset_calls += 1

    class TestDice:
        def __init__(self, game):
            self.game = game
            self.remaining = []

        def movimientos_restantes(self):
            return list(self.remaining)

        def reiniciar_turno(self):
            self.remaining = []

    class TestGame:
        def __init__(self, board=None, jugador_inicial=None):
            self.board = board
            self.dice = TestDice(self)
            self.jugador_actual = jugador_inicial
            self._moves = []
            self._ganador = None
            self.ganador = None
            self.tablero = board  # Adapter compatibility

        def movimientos_disponibles(self):
            return list(self._moves)

        def puede_mover(self, *_):
            return bool(self._moves)

        def comenzar_turno(self):
            self._moves = [(12, 10)]
            self.dice.remaining = list(self._moves)
            return True

        def realizar_movimiento(self, origen, destino):
            if (origen, destino) in self._moves or origen == -1:
                self._moves = []
                self.dice.remaining = []
                return True
            return False

        def terminar_turno(self):
            self.jugador_actual = cli_main.NEGRO if self.jugador_actual == cli_main.BLANCO else cli_main.BLANCO
            return True

        def get_ganador(self):
            return self._ganador

    monkeypatch.setattr(cli_main, "Board", TestBoard)
    monkeypatch.setattr(cli_main, "Game", TestGame)

    inputs = iter([
        "tablero",
        "barra",
        "fuera",
        "turno",
        "tirar",
        "12 10",
        "mover",
        "mover 1 x",
        "mover 2 3",
        "mover_barra",
        "mover_barra x",
        "mover_barra 4",
        "pasar",
        "reset",
        "desconocido",
        "salir",
    ])

    def fake_input(prompt=""):
        return next(inputs)

    monkeypatch.setattr("builtins.input", fake_input)
    exit_code = cli_main.main()
    assert exit_code == 0

    out = capsys.readouterr().out
    assert "Backgammon CLI" in out
    assert "Barra" in out
    assert "Turno:" in out
    assert "Partida reiniciada." in out
    assert "Comando desconocido." in out


def test_main_when_roll_already_available(monkeypatch, capsys):
    from cli import main as cli_main

    class BoardStub:
        def __init__(self):
            self.__posiciones__ = [{"color": None, "cantidad": 0} for _ in range(24)]

        def points_snapshot(self):
            return [{"color": None, "cantidad": 0} for _ in range(24)]

    class GameStub:
        def __init__(self, board=None, jugador_inicial=None):
            self.board = board
            self.dice = types.SimpleNamespace(movimientos_restantes=lambda: [(1, 2)], reiniciar_turno=lambda: None)
            self.jugador_actual = jugador_inicial
            self._moves = [(1, 2)]
            self.tablero = board
            self._ganador = None
            self.ganador = None

        def movimientos_disponibles(self):
            return list(self._moves)

        def get_ganador(self):
            return self._ganador

    monkeypatch.setattr(cli_main, "Board", BoardStub)
    monkeypatch.setattr(cli_main, "Game", GameStub)

    inputs = iter([
        "tirar",
        "salir",
    ])

    def fake_input(prompt=""):
        return next(inputs)

    monkeypatch.setattr("builtins.input", fake_input)
    cli_main.main()
    out = capsys.readouterr().out
    assert "Ya hay tiradas" in out


def test_interactuar_movimientos_full_flow(monkeypatch, capsys):
    from cli import main as cli_main

    class DummyDice:
        def __init__(self, game):
            self.game = game

        def movimientos_restantes(self):
            return list(self.game.remaining)

    class DummyGame:
        def __init__(self):
            self.jugador_actual = cli_main.BLANCO
            self.remaining = [1, 2]
            self._moves = [(1, 2), (2, 3)]
            self.dice = DummyDice(self)
            self.tablero = None
            self.board = None
            self._calls = 0

        def movimientos_disponibles(self):
            return list(self.remaining)

        def puede_mover(self, *_):
            return bool(self._moves)

        def turno_actual(self):
            return self.jugador_actual

        def realizar_movimiento(self, origen, destino):
            if (origen, destino) in self._moves:
                self._moves.remove((origen, destino))
                if self.remaining:
                    self.remaining.pop(0)
                return True
            return False

        def terminar_turno(self):
            self.jugador_actual = cli_main.NEGRO if self.jugador_actual == cli_main.BLANCO else cli_main.BLANCO
            return True

    game = DummyGame()
    inputs = iter(["", "foo", "a b", "9 8", "1 2"])

    def fake_input(prompt=""):
        try:
            return next(inputs)
        except StopIteration:
            raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", fake_input)
    cli_main._interactuar_movimientos(game)
    out = capsys.readouterr().out
    assert "Uso: <origen> <destino>" in out
    assert "Origen y destino deben ser enteros." in out
    assert "Movimiento inválido" in out
    assert "Tiradas restantes" in out
    assert out.endswith("\n")


def test_interactuar_movimientos_fin_command(monkeypatch, capsys):
    from cli import main as cli_main

    class DummyGame:
        def __init__(self):
            self.jugador_actual = cli_main.BLANCO
            self.remaining = [4]
            self._moves = [(4, 5)]
            self.dice = types.SimpleNamespace(movimientos_restantes=lambda: list(self.remaining))

        def movimientos_disponibles(self):
            return list(self.remaining)

        def puede_mover(self, *_):
            return bool(self._moves)

        def turno_actual(self):
            return self.jugador_actual

        def realizar_movimiento(self, *_):
            return False

        def terminar_turno(self):
            return True

    game = DummyGame()

    inputs = iter(["fin"])

    def fake_input(prompt=""):
        return next(inputs)

    monkeypatch.setattr("builtins.input", fake_input)
    cli_main._interactuar_movimientos(game)
    out = capsys.readouterr().out
    assert "Turno de" in out


def test_interactuar_movimientos_sin_movimientos(monkeypatch, capsys):
    from cli import main as cli_main

    class DummyGame:
        def __init__(self):
            self.jugador_actual = cli_main.BLANCO
            self.remaining = [4]
            self._first_call = True
            self.dice = types.SimpleNamespace(movimientos_restantes=lambda: list(self.remaining))

        def movimientos_disponibles(self):
            return list(self.remaining)

        def puede_mover(self, *_):
            if self._first_call:
                self._first_call = False
                return True
            return False

        def turno_actual(self):
            return self.jugador_actual

        def terminar_turno(self):
            self.jugador_actual = cli_main.NEGRO
            return True

    game = DummyGame()

    cli_main._interactuar_movimientos(game)
    out = capsys.readouterr().out
    assert "Sin movimientos. Se pasa el turno." in out


def test_cli_main_fallback_imports(monkeypatch):
    import cli.main as original_main

    path = Path(original_main.__file__)

    saved_modules = {
        key: sys.modules.get(key)
        for key in (
            "core",
            "core.board",
            "core.player",
            "core.game",
            "cli.main_fallback_test",
        )
    }

    for key in ("core", "core.board", "core.player", "core.game", "cli.main_fallback_test"):
        sys.modules.pop(key, None)

    root = Path(path).resolve().parent.parent
    if str(root) in sys.path:
        sys.path.remove(str(root))

    stub_core = types.ModuleType("core")
    sys.modules["core"] = stub_core

    core_player = types.ModuleType("core.player")
    class StubPlayer:
        pass
    core_player.Player = StubPlayer
    sys.modules["core.player"] = core_player

    core_game = types.ModuleType("core.game")
    class StubGame:
        def __init__(self, board=None, jugador_inicial=None):
            self.board = board
            self.jugador_actual = jugador_inicial
    core_game.Game = StubGame
    sys.modules["core.game"] = core_game

    core_board = types.ModuleType("core.board")
    class StubBoard:
        pass
    core_board.Board = StubBoard
    core_board.BLANCO = "board_blanco"
    core_board.NEGRO = "board_negro"
    sys.modules["core.board"] = core_board

    try:
        spec = importlib.util.spec_from_file_location("cli.main_fallback_test", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)  # type: ignore[arg-type]

        assert module.BLANCO == "board_blanco"
        assert module.NEGRO == "board_negro"
        assert module._PROJECT_ROOT in sys.path
    finally:
        sys.modules.pop("cli.main_fallback_test", None)
        for key, mod in saved_modules.items():
            if mod is not None:
                sys.modules[key] = mod
            else:
                sys.modules.pop(key, None)
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
