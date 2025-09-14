import random

class Dice:
    def __init__(self):
        self.__valor1__ = None
        self.__valor2__ = None

    def tirar(self):
        self.__valor1__ = random.randint(1, 6)
        self.__valor2__ = random.randint(1, 6)

    def obtener_valores(self):
        return (self.__valor1__, self.__valor2__)

    def es_doble(self):
        return self.__valor1__