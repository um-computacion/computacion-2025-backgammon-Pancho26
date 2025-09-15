import unittest
from core.dice import Dice

class TestDice(unittest.TestCase):
    def test_tirar_asigna_valores(self):
        dice = Dice()
        dice.tirar()
        v1, v2 = dice.__valor1__, dice.__valor2__
        self.assertTrue(1 <= v1 <= 6)
        self.assertTrue(1 <= v2 <= 6)

    def test_obtener_valores_no_doble(self):
        dice = Dice()
        dice.__valor1__ = 3
        dice.__valor2__ = 5
        valores = dice.obtener_valores()
        self.assertEqual(valores, [3, 5])

    def test_obtener_valores_doble(self):
        dice = Dice()
        dice.__valor1__ = 4
        dice.__valor2__ = 4
        valores = dice.obtener_valores()
        self.assertEqual(valores, [4, 4, 4, 4])

    def test_es_doble_true(self):
        dice = Dice()
        dice.__valor1__ = 2
        dice.__valor2__ = 2
        self.assertTrue(dice.es_doble())

    def test_es_doble_false(self):
        dice = Dice()
        dice.__valor1__ = 1
        dice.__valor2__ = 6
        self.assertFalse(dice.es_doble())

if __name__ == "__main__":
    unittest.main()