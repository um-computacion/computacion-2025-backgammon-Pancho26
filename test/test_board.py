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

if __name__ == "__main__":
    unittest.main()
