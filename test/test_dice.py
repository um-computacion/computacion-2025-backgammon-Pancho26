import unittest
import random
from core.dice import Dice

class TestDiceEstadoInicial(unittest.TestCase):
    def test_estado_inicial(self):
        d = Dice()
        self.assertEqual(d.obtener_valores(), [])
        self.assertFalse(d.quedan_movimientos())

class TestDiceTirada(unittest.TestCase):
    def test_tirar_asigna_valores(self):
        d = Dice()
        d.tirar()
        self.assertIsNotNone(d.__valor1__)
        self.assertIsNotNone(d.__valor2__)
        self.assertTrue(1 <= d.__valor1__ <= 6)
        self.assertTrue(1 <= d.__valor2__ <= 6)

    def test_tirar_dos_veces_error(self):
        d = Dice()
        d.tirar()
        with self.assertRaises(ValueError):
            d.tirar()

    def test_reiniciar_turno(self):
        d = Dice()
        d.tirar()
        d.reiniciar_turno()
        self.assertIsNone(d.__valor1__)
        self.assertIsNone(d.__valor2__)
        self.assertFalse(d.quedan_movimientos())
        d.tirar()  # no debe lanzar

class TestDiceDoblesYValores(unittest.TestCase):
    def test_es_doble_false(self):
        d = Dice()
        d.__valor1__ = 2
        d.__valor2__ = 5
        self.assertFalse(d.es_doble())
        self.assertEqual(d.obtener_valores(), [2,5])

    def test_es_doble_true(self):
        d = Dice()
        d.__valor1__ = 4
        d.__valor2__ = 4
        self.assertTrue(d.es_doble())
        self.assertEqual(d.obtener_valores(), [4,4,4,4])

class TestDiceMovimientosRestantes(unittest.TestCase):
    def test_movimientos_restantes_no_doble(self):
        rng = random.Random(1234)
        d = Dice(rng)
        d.tirar()
        self.assertEqual(d.movimientos_restantes(), d.obtener_valores())

    def test_movimientos_restantes_doble_manual(self):
        d = Dice()
        d.__valor1__ = 6
        d.__valor2__ = 6
        d.__tirado__ = True
        d.__restantes__ = [6,6,6,6]
        self.assertEqual(d.movimientos_restantes(), [6,6,6,6])

class TestDiceConsumo(unittest.TestCase):
    def test_consumir_valor_ok(self):
        d = Dice()
        d.__valor1__ = 3
        d.__valor2__ = 5
        d.__tirado__ = True
        d.__restantes__ = [3,5]
        d.consumir(3)
        self.assertEqual(d.movimientos_restantes(), [5])

    def test_consumir_valor_inexistente(self):
        d = Dice()
        d.__valor1__ = 2
        d.__valor2__ = 5
        d.__tirado__ = True
        d.__restantes__ = [2,5]
        with self.assertRaises(ValueError):
            d.consumir(4)

    def test_consumir_antes_de_tirar(self):
        d = Dice()
        with self.assertRaises(ValueError):
            d.consumir(3)

    def test_consumir_todos_valores_no_doble(self):
        d = Dice()
        d.__valor1__ = 1
        d.__valor2__ = 6
        d.__tirado__ = True
        d.__restantes__ = [1,6]
        d.consumir(1)
        d.consumir(6)
        self.assertFalse(d.quedan_movimientos())

    def test_consumir_todos_valores_doble(self):
        d = Dice()
        d.__valor1__ = 5
        d.__valor2__ = 5
        d.__tirado__ = True
        d.__restantes__ = [5,5,5,5]
        for _ in range(4):
            d.consumir(5)
        self.assertFalse(d.quedan_movimientos())

class TestDiceDeterminismo(unittest.TestCase):
    def test_determinismo_misma_semilla(self):
        seed = 42
        d1 = Dice(random.Random(seed))
        d2 = Dice(random.Random(seed))
        d1.tirar()
        d2.tirar()
        self.assertEqual(d1.__valor1__, d2.__valor1__)
        self.assertEqual(d1.__valor2__, d2.__valor2__)

class TestDiceSerializacion(unittest.TestCase):
    def test_a_dict_no_tirado(self):
        d = Dice()
        estado = d.a_dict()
        self.assertFalse(estado["tirado"])
        self.assertEqual(estado["valores"], [])
        self.assertEqual(estado["restantes"], [])

    def test_a_dict_doble(self):
        d = Dice()
        d.__valor1__ = 6
        d.__valor2__ = 6
        d.__tirado__ = True
        d.__restantes__ = [6,6,6,6]
        estado = d.a_dict()
        self.assertTrue(estado["tirado"])
        self.assertEqual(estado["valores"], [6,6,6,6])
        self.assertEqual(estado["restantes"], [6,6,6,6])

if __name__ == "__main__":
    unittest.main()