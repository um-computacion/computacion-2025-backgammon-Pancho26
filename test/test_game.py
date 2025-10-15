import unittest
from typing import Any, Dict, List

from core.game import Game, BLANCO, NEGRO, BoardPort, DicePort


class FakeDice(DicePort):
    """
    Dado determinista para tests.
    - valores_base: lista fija de dados del turno (p. ej., [3,5] o [6,6,6,6] para dobles)
    - tirar() no cambia los valores; sólo marca el turno activo si quisieras extenderlo.
    """
    def __init__(self, valores_base: List[int]) -> None:
        self._valores_base = list(valores_base)
        self._restantes: List[int] = []

    def tirar(self) -> None:
        # En este fake, tirar no altera la semilla ni randomiza; sólo confirma el estado.
        pass

    def obtener_valores(self) -> List[int]:
        return list(self._valores_base)

    def movimientos_restantes(self) -> List[int]:
        return list(self._restantes)

    def consumir(self, v: int) -> None:
        try:
            self._restantes.remove(v)
        except ValueError as e:
            raise ValueError("Valor no disponible") from e

    def quedan_movimientos(self) -> bool:
        return bool(self._restantes)

    def reiniciar_turno(self) -> None:
        # Al comenzar turno, se restablecen los movimientos restantes
        self._restantes = list(self._valores_base)

    def a_dict(self) -> Dict[str, Any]:
        return {"valores": list(self._valores_base), "restantes": list(self._restantes)}
class FakeBoard(BoardPort):
    """
    Tablero mínimo compatible con BoardPort.
    - puede_mover: se controla por bandera para simular bloqueo.
    - mover: configurable para aceptar o rechazar; registra la última llamada.
    - pasos: lógica simple + soporte de barra (-1) como en el adaptador real.
    """
    def __init__(self, puede_mover_flag: bool = True, mover_ok: bool = True) -> None:
        self.puede_mover_flag = puede_mover_flag
        self.mover_ok = mover_ok
        self.last_move = None  # (jugador, origen, destino)
        self.move_calls = 0

    def mover(self, jugador: str, origen: int, destino: int) -> bool:
        self.move_calls += 1
        self.last_move = (jugador, origen, destino)
        return bool(self.mover_ok)

    def puede_mover(self, jugador: str, valores: List[int]) -> bool:
        # Si no hay valores, no puede mover. Si hay, respeta la bandera.
        return bool(valores) and bool(self.puede_mover_flag)

    def pasos(self, jugador: str, origen: int, destino: int) -> int:
        if origen == -1:
            if jugador == BLANCO:
                if 0 <= destino <= 5:
                    return destino + 1
            else:  # NEGRO
                if 18 <= destino <= 23:
                    return 24 - destino
            raise ValueError("Destino inválido para reingreso desde barra.")
        diff = abs(int(destino) - int(origen))
        if diff <= 0:
            raise ValueError("Pasos inválidos (origen=destino).")
        return diff
class TestGameBasico(unittest.TestCase):
    def test_comenzar_turno_bloqueado_pasa(self):
        board = FakeBoard(puede_mover_flag=False)
        dice = FakeDice([3])
        g = Game(board=board, dice=dice, jugador_inicial=BLANCO)
        pudo = g.comenzar_turno()
        self.assertFalse(pudo)
        self.assertEqual(g.jugador_actual, NEGRO)  # pasó el turno

    def test_comenzar_turno_con_movimientos(self):
        board = FakeBoard(puede_mover_flag=True)
        dice = FakeDice([3, 5])
        g = Game(board=board, dice=dice, jugador_inicial=NEGRO)
        pudo = g.comenzar_turno()
        self.assertTrue(pudo)
        self.assertEqual(g.jugador_actual, NEGRO)
        self.assertEqual(g.movimientos_disponibles(), [3, 5])

    def test_realizar_movimiento_consumo_y_ok(self):
        board = FakeBoard(puede_mover_flag=True, mover_ok=True)
        dice = FakeDice([3, 5])
        g = Game(board=board, dice=dice, jugador_inicial=BLANCO)
        self.assertTrue(g.comenzar_turno())
        ok = g.realizar_movimiento(0, 3)  # pasos = 3
        self.assertTrue(ok)
        self.assertEqual(board.last_move, (BLANCO, 0, 3))
        self.assertEqual(g.movimientos_disponibles(), [5])

    def test_realizar_movimiento_sin_movimientos_lanza_error(self):
        board = FakeBoard(puede_mover_flag=True, mover_ok=True)
        dice = FakeDice([])  # sin dados en este turno
        g = Game(board=board, dice=dice, jugador_inicial=BLANCO)
        # No comenzamos turno; no hay movimientos restantes
        with self.assertRaises(ValueError):
            g.realizar_movimiento(0, 1)
        self.assertEqual(board.move_calls, 0)

    def test_realizar_movimiento_dado_no_coincide(self):
        board = FakeBoard(puede_mover_flag=True, mover_ok=True)
        dice = FakeDice([2])  # sólo dado 2 disponible
        g = Game(board=board, dice=dice, jugador_inicial=BLANCO)
        self.assertTrue(g.comenzar_turno())
        # Intento de 0 -> 3 requiere dado 3, que no está
        with self.assertRaises(ValueError):
            g.realizar_movimiento(0, 3)
        self.assertEqual(board.move_calls, 0)  # no llegó a llamar a mover

    def test_realizar_movimiento_rechazado_por_board_no_consumir(self):
        board = FakeBoard(puede_mover_flag=True, mover_ok=False)
        dice = FakeDice([4])
        g = Game(board=board, dice=dice, jugador_inicial=BLANCO)
        self.assertTrue(g.comenzar_turno())
        with self.assertRaises(ValueError):
            g.realizar_movimiento(0, 4)  # pasos=4 coincide, pero el board rechaza
        # No debe consumir el dado si el tablero rechaza
        self.assertEqual(g.movimientos_disponibles(), [4])
        self.assertEqual(board.move_calls, 1)

    def test_movimiento_desde_barra_blanco(self):
        board = FakeBoard(puede_mover_flag=True, mover_ok=True)
        dice = FakeDice([6])
        g = Game(board=board, dice=dice, jugador_inicial=BLANCO)
        self.assertTrue(g.comenzar_turno())
        ok = g.realizar_movimiento(-1, 5)  # reingreso blanco: destino 5 => pasos 6
        self.assertTrue(ok)
        self.assertEqual(board.last_move, (BLANCO, -1, 5))
        self.assertEqual(g.movimientos_disponibles(), [])

    def test_movimiento_desde_barra_negro(self):
        board = FakeBoard(puede_mover_flag=True, mover_ok=True)
        dice = FakeDice([6])
        g = Game(board=board, dice=dice, jugador_inicial=NEGRO)
        self.assertTrue(g.comenzar_turno())
        ok = g.realizar_movimiento(-1, 18)  # reingreso negro: destino 18 => pasos 6
        self.assertTrue(ok)
        self.assertEqual(board.last_move, (NEGRO, -1, 18))
        self.assertEqual(g.movimientos_disponibles(), [])

    def test_terminar_turno_cambia_jugador_y_reinicia_dados(self):
        board = FakeBoard(puede_mover_flag=True, mover_ok=True)
        dice = FakeDice([1, 2])
        g = Game(board=board, dice=dice, jugador_inicial=BLANCO)
        self.assertTrue(g.comenzar_turno())
        # Consumimos uno para verificar que luego se reinicia
        g.realizar_movimiento(0, 1)
        self.assertEqual(g.movimientos_disponibles(), [2])
        g.terminar_turno()
        self.assertEqual(g.jugador_actual, NEGRO)
        # Reinició el turno de los dados (restaura a [1,2] por nuestro Fake)
        self.assertEqual(g.movimientos_disponibles(), [1, 2])

    def test_a_dict_estructura_minima(self):
        board = FakeBoard(puede_mover_flag=True, mover_ok=True)
        dice = FakeDice([3, 3, 3, 3])  # simular dobles
        g = Game(board=board, dice=dice, jugador_inicial=BLANCO)
        self.assertTrue(g.comenzar_turno())
        data = g.a_dict()
        self.assertIn("jugador_actual", data)
        self.assertIn("dados", data)
        self.assertIn("movimientos_disponibles", data)
        self.assertEqual(data["jugador_actual"], BLANCO)
        self.assertEqual(data["movimientos_disponibles"], [3, 3, 3, 3])


if __name__ == "__main__":
    unittest.main()