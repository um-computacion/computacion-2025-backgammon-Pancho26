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


class TestGameExtraCoverage(unittest.TestCase):
    def test_comenzar_turno_sin_tiradas_pasa_turno(self):
        # dados sin valores -> puede_mover() False => pasa el turno
        class EmptyDice(DicePort):  # type: ignore[misc]
            def __init__(self) -> None:
                self._rest: List[int] = []
            def tirar(self) -> None: pass
            def obtener_valores(self) -> List[int]: return []
            def movimientos_restantes(self) -> List[int]: return list(self._rest)
            def consumir(self, v: int) -> None: raise AssertionError("no debería consumir")
            def quedan_movimientos(self) -> bool: return False
            def reiniciar_turno(self) -> None: self._rest = []
            def a_dict(self) -> Dict[str, Any]: return {"valores": [], "restantes": []}

        class YesBoard(BoardPort):  # type: ignore[misc]
            def mover(self, jugador: str, origen: int, destino: int) -> bool: return True
            def puede_mover(self, jugador: str, valores: List[int]) -> bool: return True
            def pasos(self, jugador: str, origen: int, destino: int) -> int: return abs(destino - origen) or 1

        g = Game(board=YesBoard(), dice=EmptyDice(), jugador_inicial=BLANCO)
        self.assertFalse(g.comenzar_turno())
        self.assertEqual(g.jugador_actual, NEGRO)

    def test_adapter_con_board_real_mov_normal(self):
        # Cubre BoardAdapter con Board real (aplicar_movimiento/es_movimiento_legal)
        from core.board import Board
        b = Board()
        # Asegurar movimiento simple BLANCO: 0 -> 1 con dado 1
        dice = FakeDice([1])
        g = Game(board=b, dice=dice, jugador_inicial=BLANCO)  # usa BoardAdapter internamente
        self.assertTrue(g.comenzar_turno())
        ok = g.realizar_movimiento(0, 1)
        self.assertTrue(ok)
        # Verificar que el punto 1 ahora tiene una blanca (usamos API del Board real)
        self.assertEqual(b.top_color_at(1), BLANCO)

    def test_adapter_fallback_mover_ficha_sin_aplicar_movimiento(self):
        # Cubre la rama de fallback a mover_ficha en BoardAdapter.mover
        calls: List[tuple[int, int]] = []
        class MinimalBoard:  # sin es_movimiento_legal ni aplicar_movimiento
            def mover_ficha(self, origen: int, destino: int) -> None:
                calls.append((origen, destino))
        mb = MinimalBoard()
        dice = FakeDice([3])
        g = Game(board=mb, dice=dice, jugador_inicial=BLANCO)  # envuelve con BoardAdapter
        self.assertTrue(g.comenzar_turno())
        self.assertTrue(g.realizar_movimiento(0, 3))
        self.assertEqual(calls, [(0, 3)])
        self.assertEqual(g.movimientos_disponibles(), [])

    def test_adapter_fallback_mover_desde_barra_true_y_false(self):
        # Cubre la rama origen == -1 con mover_desde_barra
        class BoardBarOK:
            def __init__(self, ok: bool) -> None:
                self.ok = ok
                self.calls: List[tuple[str, int]] = []
            def mover_desde_barra(self, color: str, destino: int) -> bool:
                self.calls.append((color, destino))
                return self.ok

        # Caso OK
        dice_ok = FakeDice([6])
        bb_ok = BoardBarOK(ok=True)
        g_ok = Game(board=bb_ok, dice=dice_ok, jugador_inicial=BLANCO)
        self.assertTrue(g_ok.comenzar_turno())
        self.assertTrue(g_ok.realizar_movimiento(-1, 5))  # BLANCO: destino 5 => pasos 6
        self.assertEqual(bb_ok.calls, [(BLANCO, 5)])
        self.assertEqual(g_ok.movimientos_disponibles(), [])

        # Caso rechazado por el board -> no consumir
        dice_no = FakeDice([6])
        bb_no = BoardBarOK(ok=False)
        g_no = Game(board=bb_no, dice=dice_no, jugador_inicial=NEGRO)
        self.assertTrue(g_no.comenzar_turno())
        with self.assertRaises(ValueError):
            g_no.realizar_movimiento(-1, 18)  # NEGRO: destino 18 => pasos 6
        self.assertEqual(g_no.movimientos_disponibles(), [6])
        self.assertEqual(bb_no.calls, [(NEGRO, 18)])

    def test_adapter_pasos_barra_invalidos_no_consumen(self):
        # pasos() del adaptador debe lanzar si el destino no corresponde a barra
        class DumbBoard:
            # No necesita implementar nada más; sólo se envuelve por el adaptador
            pass
        dice = FakeDice([4])
        g = Game(board=DumbBoard(), dice=dice, jugador_inicial=BLANCO)
        self.assertTrue(g.comenzar_turno())
        with self.assertRaises(ValueError):
            g.realizar_movimiento(-1, 10)  # destino inválido para reingreso BLANCO
        self.assertEqual(g.movimientos_disponibles(), [4])  # no consumido

    def test_puede_mover_directo_false_y_true(self):
        # Cubre puede_mover() usando valores del dado y respuesta del board
        class PMBoard(BoardPort):  # type: ignore[misc]
            def __init__(self, flag: bool) -> None:
                self.flag = flag
            def mover(self, jugador: str, origen: int, destino: int) -> bool: return True
            def puede_mover(self, jugador: str, valores: List[int]) -> bool: return self.flag and bool(valores)
            def pasos(self, jugador: str, origen: int, destino: int) -> int: return abs(destino - origen) or 1

        dice = FakeDice([2])
        g = Game(board=PMBoard(False), dice=dice, jugador_inicial=BLANCO)
        self.assertFalse(g.puede_mover())
        g2 = Game(board=PMBoard(True), dice=dice, jugador_inicial=BLANCO)
        self.assertTrue(g2.puede_mover())


class TestGameMoreBranches(unittest.TestCase):
    def test_pasos_origen_destino_igual_no_consumir(self):
        # calcular_pasos() debe lanzar si origen==destino; no debe llamar a mover ni consumir
        class NoopBoard(BoardPort):  # type: ignore[misc]
            def mover(self, jugador: str, origen: int, destino: int) -> bool:
                raise AssertionError("No debería llamarse mover si pasos falla")
            def puede_mover(self, jugador: str, valores: List[int]) -> bool:
                return True
            def pasos(self, jugador: str, origen: int, destino: int) -> int:
                diff = abs(destino - origen)
                if diff <= 0:
                    raise ValueError("Origen y destino deben ser distintos")
                return diff

        dice = FakeDice([3])
        g = Game(board=NoopBoard(), dice=dice, jugador_inicial=BLANCO)
        self.assertTrue(g.comenzar_turno())
        with self.assertRaises(ValueError):
            g.realizar_movimiento(5, 5)
        # No consumió el dado
        self.assertEqual(g.movimientos_disponibles(), [3])

    def test_adapter_es_movimiento_legal_false_rechaza(self):
        # BoardAdapter debe rechazar sin aplicar cuando es_movimiento_legal == False
        class BoardLegalFalse:
            def __init__(self) -> None:
                self.aplicar_llamadas = 0
            def es_movimiento_legal(self, origen: int, destino: int, color: str) -> bool:
                return False
            def aplicar_movimiento(self, origen: int, destino: int, color: str) -> bool:
                self.aplicar_llamadas += 1
                return True  # no debería ejecutarse

        b = BoardLegalFalse()
        g = Game(board=b, dice=FakeDice([1]), jugador_inicial=BLANCO)
        self.assertTrue(g.comenzar_turno())
        with self.assertRaises(ValueError):
            g.realizar_movimiento(0, 1)
        # No consumió y no aplicó
        self.assertEqual(g.movimientos_disponibles(), [1])
        self.assertEqual(b.aplicar_llamadas, 0)

    def test_adapter_aplicar_movimiento_lanza_excepcion(self):
        # BoardAdapter debe capturar la excepción y devolver False; Game lanza y no consume
        class BoardRaises:
            def aplicar_movimiento(self, origen: int, destino: int, color: str) -> bool:
                raise RuntimeError("Falla interna")
        g = Game(board=BoardRaises(), dice=FakeDice([2]), jugador_inicial=NEGRO)
        self.assertTrue(g.comenzar_turno())
        with self.assertRaises(ValueError):
            g.realizar_movimiento(0, 2)
        self.assertEqual(g.movimientos_disponibles(), [2])


class TestGameEvenMoreCoverage(unittest.TestCase):
    def test_adapter_aplicar_movimiento_false_rechaza(self):
        # Cuando es_movimiento_legal=True pero aplicar_movimiento=False, debe rechazar sin consumir
        class BoardLegalButApplyFalse:
            def __init__(self) -> None:
                self.legal_calls = 0
                self.apply_calls = 0
            def es_movimiento_legal(self, origen: int, destino: int, color: str) -> bool:
                self.legal_calls += 1
                return True
            def aplicar_movimiento(self, origen: int, destino: int, color: str) -> bool:
                self.apply_calls += 1
                return False

        b = BoardLegalButApplyFalse()
        g = Game(board=b, dice=FakeDice([1]), jugador_inicial=BLANCO)
        self.assertTrue(g.comenzar_turno())
        with self.assertRaises(ValueError):
            g.realizar_movimiento(0, 1)
        # No debe consumir el dado
        self.assertEqual(g.movimientos_disponibles(), [1])
        # Validación y aplicar fueron invocados
        self.assertEqual(b.legal_calls, 1)
        self.assertEqual(b.apply_calls, 1)

    def test_puede_mover_sin_valores_de_dado(self):
        # Si los dados no tienen valores, puede_mover() debe ser False sin consultar al board
        class BoardSpy(BoardPort):  # type: ignore[misc]
            def __init__(self) -> None:
                self.calls = 0
            def mover(self, jugador: str, origen: int, destino: int) -> bool:
                self.calls += 1
                return False
            def puede_mover(self, jugador: str, valores: List[int]) -> bool:
                self.calls += 1
                return True
            def pasos(self, jugador: str, origen: int, destino: int) -> int:
                return abs(destino - origen) or 1

        class EmptyDice(DicePort):  # type: ignore[misc]
            def tirar(self) -> None: ...
            def obtener_valores(self) -> List[int]: return []
            def movimientos_restantes(self) -> List[int]: return []
            def consumir(self, v: int) -> None: raise AssertionError("no debe consumir")
            def quedan_movimientos(self) -> bool: return False
            def reiniciar_turno(self) -> None: ...
            def a_dict(self) -> Dict[str, Any]: return {"valores": [], "restantes": []}

        spy = BoardSpy()
        g = Game(board=spy, dice=EmptyDice(), jugador_inicial=NEGRO)
        self.assertFalse(g.puede_mover())
        # No debería haber llamado al board
        self.assertEqual(spy.calls, 0)

    def test_adapter_mover_sin_api_devuelve_false(self):
        # Objeto Board vacío (sin métodos). El adaptador debe devolver False, y Game no consume dado.
        class EmptyBoard:
            pass

        g = Game(board=EmptyBoard(), dice=FakeDice([2]), jugador_inicial=BLANCO)
        self.assertTrue(g.comenzar_turno())  # fallback puede_mover -> True por valores presentes
        with self.assertRaises(ValueError):
            g.realizar_movimiento(0, 2)  # mover() => False por falta de API
        # Dado sigue disponible (no se consumió)
        self.assertEqual(g.movimientos_disponibles(), [2])


if __name__ == "__main__":
    unittest.main()