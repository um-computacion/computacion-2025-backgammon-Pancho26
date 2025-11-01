import unittest
from core.board import Board

BLANCO = "blanco"
NEGRO = "negro"

class TestBoardInicial(unittest.TestCase):
    def test_inicializacion_estandar(self):
        b = Board()
        self.assertEqual(len(b.obtener_punto(0)), 2)
        self.assertEqual(len(b.obtener_punto(11)), 5)
        self.assertEqual(len(b.obtener_punto(16)), 3)
        self.assertEqual(len(b.obtener_punto(18)), 5)
        self.assertEqual(len(b.obtener_punto(23)), 2)
        self.assertEqual(len(b.obtener_punto(12)), 5)
        self.assertEqual(len(b.obtener_punto(7)), 3)
        self.assertEqual(len(b.obtener_punto(5)), 5)

class TestMovimientoLegal(unittest.TestCase):
    def setUp(self):
        self.b = Board()

    def test_movimiento_normal_legal(self):
        origen = 0
        tirada = 2
        destino = self.b.calcular_destino(origen, BLANCO, tirada)
        self.assertTrue(self.b.es_movimiento_legal(origen, destino, BLANCO))

    def test_bloqueo_por_doble_rival(self):
        self.b.__posiciones__[3] = [NEGRO, NEGRO]
        self.assertFalse(self.b.es_movimiento_legal(0, 3, BLANCO))

    def test_origen_vacio(self):
        self.assertFalse(self.b.es_movimiento_legal(2, 3, BLANCO))

    def test_origen_de_otro_color(self):
        self.assertFalse(self.b.es_movimiento_legal(23, 22, BLANCO))

    def test_destino_fuera_de_rango(self):
        self.assertFalse(self.b.es_movimiento_legal(0, 24, BLANCO))
        self.assertFalse(self.b.es_movimiento_legal(5, -1, BLANCO))

class TestCapturaYBarra(unittest.TestCase):
    def setUp(self):
        self.b = Board()
        # Limpiar puntos para el escenario
        self.b.__posiciones__[9] = []
        self.b.__posiciones__[10] = []

    def test_captura_en_mov_normal(self):
        self.b.agregar_ficha(10, NEGRO)      # blot negro
        self.b.agregar_ficha(9, BLANCO)      # blanca lista para capturar
        self.assertTrue(self.b.es_movimiento_legal(9, 10, BLANCO))
        self.b.mover_ficha(9, 10)
        self.assertEqual(self.b.obtener_barra(NEGRO), [NEGRO])
        self.assertEqual(self.b.obtener_punto(10), [BLANCO])

    def test_reingreso_desde_barra_bloqueado(self):
        self.b.__barra__[NEGRO].append(NEGRO)
        self.b.__posiciones__[23] = [BLANCO, BLANCO]  # bloqueado para negras con 1
        destino = self.b.calcular_destino_barra(NEGRO, 1)  # 23
        self.assertFalse(self.b.es_movimiento_legal(-1, destino, NEGRO))

    def test_reingreso_desde_barra_con_captura(self):
        self.b.__barra__[NEGRO].append(NEGRO)
        destino = self.b.calcular_destino_barra(NEGRO, 1)  # 23
        self.b.__posiciones__[destino] = [BLANCO]  # blot blanco
        ok = self.b.mover_desde_barra(NEGRO, destino)
        self.assertTrue(ok)
        self.assertEqual(self.b.obtener_barra(BLANCO), [BLANCO])
        self.assertEqual(self.b.obtener_punto(destino), [NEGRO])

class TestPuedeMover(unittest.TestCase):
    def setUp(self):
        self.b = Board()

    def test_puede_mover_con_barra_bloqueado(self):
        # Todas las entradas de blanco bloqueadas 1..6
        self.b.__barra__[BLANCO].append(BLANCO)
        for i in range(6):  # puntos 0..5
            self.b.__posiciones__[i] = [NEGRO, NEGRO]
        self.assertFalse(self.b.puede_mover(BLANCO, [1,2,3,4,5,6]))

    def test_puede_mover_con_barra_hay_hueco(self):
        self.b.__barra__[BLANCO].append(BLANCO)
        for i in range(6):
            self.b.__posiciones__[i] = [NEGRO, NEGRO]
        # Abrimos el punto 2 (tirada 3 -> índice 2)
        self.b.__posiciones__[2] = []
        self.assertTrue(self.b.puede_mover(BLANCO, [3]))

class TestDestinos(unittest.TestCase):
    def setUp(self):
        self.b = Board()

    def test_calcular_destino_blanco(self):
        self.assertEqual(self.b.calcular_destino(0, BLANCO, 3), 3)

    def test_calcular_destino_negro(self):
        self.assertEqual(self.b.calcular_destino(23, NEGRO, 3), 20)

    def test_calcular_destino_barra_blanco(self):
        self.assertEqual(self.b.calcular_destino_barra(BLANCO, 6), 5)

    def test_calcular_destino_barra_negro(self):
        self.assertEqual(self.b.calcular_destino_barra(NEGRO, 6), 18)

class TestBornear(unittest.TestCase):
    def setUp(self):
        self.b = Board()
        self.b.__posiciones__[0] = [BLANCO]

    def test_bornear_basico(self):
        self.b.bornear_ficha(0, BLANCO)
        self.assertEqual(self.b.obtener_fuera(BLANCO), [BLANCO])
        self.assertEqual(self.b.obtener_punto(0), [])

class TestHelpersUI(unittest.TestCase):
    def test_obtener_estado_puntos(self):
        b = Board()
        estado = b.obtener_estado_puntos()
        self.assertEqual(len(estado), 24)
        self.assertIn("color", estado[0])
        self.assertIn("cantidad", estado[0])

class TestAplicarMovimiento(unittest.TestCase):
    def setUp(self):
        self.b = Board()

    def test_aplicar_movimiento_normal(self):
        # Asegurar destino libre
        self.b.__posiciones__[2] = []
        # Asegurar origen con blanca
        self.b.__posiciones__[0] = [BLANCO]
        self.assertTrue(self.b.es_movimiento_legal(0, 2, BLANCO))
        ok = self.b.aplicar_movimiento(0, 2, BLANCO)
        self.assertTrue(ok)
        self.assertEqual(self.b.obtener_punto(2), [BLANCO])

    def test_aplicar_movimiento_barra(self):
        self.b.__barra__[NEGRO].append(NEGRO)
        destino = self.b.calcular_destino_barra(NEGRO, 1)  # 23
        # Asegurar destino libre
        self.b.__posiciones__[destino] = []
        ok = self.b.aplicar_movimiento(-1, destino, NEGRO)
        self.assertTrue(ok)
        self.assertEqual(self.b.obtener_punto(destino), [NEGRO])
        self.assertEqual(self.b.obtener_barra(NEGRO), [])

class TestAliasesAndCounts(unittest.TestCase):
    def setUp(self):
        self.b = Board()

    def test_aliases_reflect_changes(self):
        # Cambios por alias se ven en getters
        self.b.__posiciones__[4] = [BLANCO, BLANCO]
        self.assertEqual(self.b.obtener_punto(4), [BLANCO, BLANCO])
        self.b.__barra__[NEGRO].append(NEGRO)
        self.assertEqual(self.b.obtener_barra(NEGRO), [NEGRO])
        self.b.__fichas_fuera__[BLANCO].append(BLANCO)
        self.assertEqual(self.b.obtener_fuera(BLANCO), [BLANCO])

    def test_total_checkers_inicial(self):
        self.assertEqual(self.b.total_checkers(), 30)
        self.assertEqual(self.b.total_checkers("blanco"), 15)
        self.assertEqual(self.b.total_checkers("negro"), 15)

    def test_contar_en_barra(self):
        self.assertEqual(self.b.contar_en_barra(BLANCO), 0)
        self.b.__barra__[BLANCO].append(BLANCO)
        self.assertEqual(self.b.contar_en_barra(BLANCO), 1)


class TestTopAndSnapshots(unittest.TestCase):
    def setUp(self):
        self.b = Board()

    def test_top_color_at_vacio_y_no_vacio(self):
        self.b.__posiciones__[8] = []
        self.assertIsNone(self.b.top_color_at(8))
        self.b.__posiciones__[8] = [NEGRO, NEGRO]
        self.assertEqual(self.b.top_color_at(8), NEGRO)

    def test_points_snapshot_matches_state(self):
        self.b.__posiciones__[3] = [NEGRO, NEGRO]
        snap = self.b.obtener_estado_puntos()
        self.assertEqual(len(snap), 24)
        self.assertEqual(snap[3]["color"], NEGRO)
        self.assertEqual(snap[3]["cantidad"], 2)


class TestHomeAndDirection(unittest.TestCase):
    def setUp(self):
        self.b = Board()

    def test_is_home_point(self):
        self.assertTrue(self.b.is_home_point(BLANCO, 18))
        self.assertTrue(self.b.is_home_point(BLANCO, 23))
        self.assertFalse(self.b.is_home_point(BLANCO, 17))
        self.assertTrue(self.b.is_home_point(NEGRO, 0))
        self.assertTrue(self.b.is_home_point(NEGRO, 5))
        self.assertFalse(self.b.is_home_point(NEGRO, 6))

    def test_direction_values_and_invalid(self):
        self.assertEqual(self.b.direction(BLANCO), +1)
        self.assertEqual(self.b.direction(NEGRO), -1)
        with self.assertRaises(ValueError):
            self.b.direction("otro")


class TestBarAndOffOps(unittest.TestCase):
    def setUp(self):
        self.b = Board()

    def test_push_pop_bar_and_counts(self):
        self.b.push_to_bar(BLANCO)
        self.assertEqual(self.b.contar_en_barra(BLANCO), 1)
        popped = self.b.pop_from_bar(BLANCO)
        self.assertEqual(popped, BLANCO)
        self.assertEqual(self.b.contar_en_barra(BLANCO), 0)
        self.assertIsNone(self.b.pop_from_bar(BLANCO))  # vacío

    def test_bar_and_off_return_copies(self):
        barra_copia = self.b.obtener_barra()
        fuera_copia = self.b.obtener_fuera()
        barra_copia[BLANCO].append(BLANCO)
        fuera_copia[NEGRO].append(NEGRO)
        self.assertEqual(self.b.contar_en_barra(BLANCO), 0)
        self.assertEqual(self.b.borne_off_count(NEGRO), 0)

    def test_push_borne_off_and_ha_ganado(self):
        for _ in range(15):
            self.b.push_borne_off(BLANCO)
        self.assertEqual(self.b.borne_off_count(BLANCO), 15)
        self.assertTrue(self.b.ha_ganado(BLANCO))


class TestClone(unittest.TestCase):
    def test_clone_independence_and_aliases(self):
        b = Board()
        c = b.clone()
        # Independencia
        b.__posiciones__[0] = [NEGRO]  # cambiar a un valor distinto del estado inicial del clon
        self.assertNotEqual(b.obtener_punto(0), c.obtener_punto(0))
        c.__posiciones__[1] = [NEGRO]
        self.assertNotEqual(b.obtener_punto(1), c.obtener_punto(1))
        # Aliases existen
        self.assertIsInstance(c.__posiciones__, list)
        self.assertIsInstance(c.__barra__, dict)
        self.assertIsInstance(c.__fichas_fuera__, dict)


class TestCalculosYValidaciones(unittest.TestCase):
    def setUp(self):
        self.b = Board()

    def test_calcular_destino_invalidos(self):
        with self.assertRaises(IndexError):
            self.b.calcular_destino(-1, BLANCO, 1)
        with self.assertRaises(ValueError):
            self.b.calcular_destino(0, "otro", 1)
        with self.assertRaises(ValueError):
            self.b.calcular_destino_barra("otro", 1)

    def test_es_movimiento_legal_desde_barra_sin_fichas(self):
        destino = self.b.calcular_destino_barra(BLANCO, 1)
        self.assertFalse(self.b.es_movimiento_legal(-1, destino, BLANCO))

    def test_bornear_ficha_color_incorrecto_revierte(self):
        self.b.__posiciones__[0] = [NEGRO]
        self.b.bornear_ficha(0, BLANCO)
        self.assertEqual(self.b.obtener_punto(0), [NEGRO])

    def test_inicializar_posiciones_resetea(self):
        # Ensuciar y resetear
        self.b.__posiciones__[0] = []
        self.b.__barra__[BLANCO].append(BLANCO)
        self.b.__fichas_fuera__[NEGRO].append(NEGRO)
        self.b.inicializar_posiciones()
        self.assertEqual(len(self.b.obtener_punto(0)), 2)
        self.assertEqual(self.b.obtener_barra(BLANCO), [])
        self.assertEqual(self.b.obtener_fuera(NEGRO), [])

    def test_aplicar_movimiento_barra_bloqueado(self):
        self.b.__barra__[BLANCO].append(BLANCO)
        destino = self.b.calcular_destino_barra(BLANCO, 1)  # 0
        self.b.__posiciones__[destino] = [NEGRO, NEGRO]
        self.assertFalse(self.b.es_movimiento_legal(-1, destino, BLANCO))
        ok = self.b.aplicar_movimiento(-1, destino, BLANCO)
        self.assertFalse(ok)

if __name__ == "__main__":
    unittest.main()
