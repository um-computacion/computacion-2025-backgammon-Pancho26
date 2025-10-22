import pytest
from core.player import Player, BLANCO, NEGRO


class DummyRng:
    def __init__(self, seq):
        self._it = iter(seq)

    def randint(self, a, b):
        return next(self._it)


class FakeBoard:
    def __init__(self):
        self.can_move_result = True
        self.legal = True
        self.apply_result = 1
        self.raise_on_calc = False
        self.raise_on_calc_barra = False
        self.bornear_raises = False

    # Consultas
    def puede_mover(self, color, tiradas):
        self.last_puede_mover = (color, list(tiradas))
        return self.can_move_result

    def direction(self, color):
        return 1 if color == BLANCO else -1

    # Movimiento
    def calcular_destino(self, origen, color, paso):
        if self.raise_on_calc:
            raise Exception("calc error")
        return origen + paso * self.direction(color)

    def calcular_destino_barra(self, color, paso):
        if self.raise_on_calc_barra:
            raise Exception("calc barra error")
        return 0  # cualquier índice válido

    def es_movimiento_legal(self, origen, destino, color):
        self.last_legal = (origen, destino, color)
        return self.legal

    def aplicar_movimiento(self, origen, destino, color):
        self.last_apply = (origen, destino, color)
        return self.apply_result

    # Bear-off
    def bornear_ficha(self, origen, color):
        if self.bornear_raises:
            raise Exception("no se puede bornear")
        self.last_bornear = (origen, color)


def test_init_valido_e_invalido():
    p = Player(BLANCO, nombre="Ana")
    assert p.color == BLANCO and p.nombre == "Ana"

    with pytest.raises(ValueError) as exc:
        Player("rojo")
    assert "Color inválido" in str(exc.value)


def test_tirar_dados_no_dobles_y_dobles():
    p = Player(NEGRO)
    assert p.tirar_dados(DummyRng([3, 5])) == [3, 5]
    assert p.tirar_dados(DummyRng([4, 4])) == [4, 4, 4, 4]


def test_roll_dice_alias():
    p = Player(BLANCO)
    assert p.roll_dice(DummyRng([2, 6])) == [2, 6]


def test_consultas_can_move_y_direction():
    p_b = Player(BLANCO)
    p_n = Player(NEGRO)
    board = FakeBoard()

    board.can_move_result = True
    assert p_b.puede_mover(board, [1, 2]) is True
    assert p_b.can_move(board, [1, 2]) is True

    board.can_move_result = False
    assert p_b.puede_mover(board, [6]) is False

    assert p_b.direccion(board) == 1
    assert p_b.direction(board) == 1
    assert p_n.direccion(board) == -1


def test_mover_exitoso_e_ilegal():
    p = Player(BLANCO)
    board = FakeBoard()

    board.legal = True
    board.apply_result = 1
    assert p.mover(board, origen=0, paso=3) is True
    assert p.move(board, origin=1, die=2) is True

    board.legal = False
    assert p.mover(board, origen=0, paso=3) is False


def test_mover_con_excepcion_en_calculo():
    p = Player(NEGRO)
    board = FakeBoard()
    board.raise_on_calc = True
    assert p.mover(board, origen=5, paso=2) is False


def test_mover_desde_barra():
    p = Player(BLANCO)
    board = FakeBoard()

    board.raise_on_calc_barra = False
    board.legal = True
    assert p.mover(board, origen=-1, paso=3) is True

    board.raise_on_calc_barra = True
    assert p.mover(board, origen=-1, paso=4) is False


def test_bornear_y_alias():
    p = Player(NEGRO)
    board = FakeBoard()

    board.bornear_raises = False
    assert p.bornear(board, origen=22) is True
    assert p.bear_off(board, origin=22) is True

    board.bornear_raises = True
    assert p.bornear(board, origen=22) is False
