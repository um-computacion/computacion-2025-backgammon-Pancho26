import unittest
from core.board import Board

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_inicializacion_posiciones(self):
        self.assertEqual(self.board.__posiciones__[0], ["blanco", "blanco"])
        self.assertEqual(self.board.__posiciones__[11], ["blanco"] * 5)
        self.assertEqual(self.board.__posiciones__[23], ["negro", "negro"])
        self.assertEqual(self.board.__posiciones__[5], ["negro"] * 5)

    def test_agregar_quitar_ficha(self):
        self.board.agregar_ficha(0, "blanco")
        self.assertEqual(self.board.__posiciones__[0][-1], "blanco")
        ficha = self.board.quitar_ficha(0)
        self.assertEqual(ficha, "blanco")

    def test_mover_ficha(self):
        self.board.agregar_ficha(1, "blanco")
        self.board.mover_ficha(1, 2)
        self.assertIn("blanco", self.board.__posiciones__[2])
        self.assertNotIn("blanco", self.board.__posiciones__[1])

    def test_captura_ficha(self):
        self.board.__posiciones__[3] = ["negro"]
        self.board.__posiciones__[2] = ["blanco"]
        self.board.mover_ficha(2, 3)
        self.assertIn("blanco", self.board.__posiciones__[3])
        self.assertIn("negro", self.board.__barra__["negro"])

    def test_es_movimiento_legal(self):
        self.assertTrue(self.board.es_movimiento_legal(0, 1, "blanco"))
        self.board.__posiciones__[1] = ["negro", "negro"]
        self.assertFalse(self.board.es_movimiento_legal(0, 1, "blanco"))

    def test_bornear_ficha(self):
        self.board.__posiciones__[23] = ["negro"]
        self.board.bornear_ficha(23, "negro")
        self.assertIn("negro", self.board.__fichas_fuera__["negro"])

    def test_puede_mover(self):
        tiradas = [1, 2, 3, 4, 5, 6]
        self.assertTrue(self.board.puede_mover("blanco", tiradas))
        self.board.__posiciones__ = [[] for _ in range(24)]
        self.assertFalse(self.board.puede_mover("blanco", tiradas))

if __name__ == "__main__":
    unittest.main()

