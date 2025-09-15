import random

class __Dice__:
    def __init__(self, rng=None):
        self.__rng__ = rng or random.Random()
        self.__valor1__ = None
        self.__valor2__ = None
        self.__tirado__ = False
        self.__restantes__ = []

    def tirar(self):
        if self.__tirado__:
            raise ValueError("Los dados ya fueron tirados este turno.")
        self.__valor1__ = self.__rng__.randint(1, 6)
        self.__valor2__ = self.__rng__.randint(1, 6)
        self.__tirado__ = True
        if self.es_doble():
            self.__restantes__ = [self.__valor1__] * 4
        else:
            self.__restantes__ = [self.__valor1__, self.__valor2__]

    def es_doble(self):
        if self.__valor1__ is None or self.__valor2__ is None:
            return False
        return self.__valor1__ == self.__valor2__

    def obtener_valores(self):
        
        if self.__valor1__ is None or self.__valor2__ is None:
            return []
        if self.es_doble():
            return [self.__valor1__] * 4
        return [self.__valor1__, self.__valor2__]

    def movimientos_restantes(self):
        return list(self.__restantes__)

    def consumir(self, valor):
        if self.__valor1__ is None or self.__valor2__ is None:
            raise ValueError("No se puede consumir antes de tirar.")
        try:
            self.__restantes__.remove(valor)
        except ValueError as exc:
            raise ValueError(f"El valor {valor} no está disponible.") from exc

    def quedan_movimientos(self):
        return bool(self.__restantes__)

    def reiniciar_turno(self):
        self.__valor1__ = None
        self.__valor2__ = None
        self.__tirado__ = False
        self.__restantes__.clear()

    def a_dict(self):
        return {
            "tirado": self.__tirado__,
            "valor1": self.__valor1__,
            "valor2": self.__valor2__,
            "valores": self.obtener_valores(),
            "restantes": list(self.__restantes__),
        }

Dice = __Dice__