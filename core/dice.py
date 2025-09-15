"""
Maneja los dados del turno:
- Tirar dos dados (o cuatro usos si es doble)
- Consultar valores
- Consumir valores
- Reiniciar para el próximo turno
"""

import random

class __Dice__:
    """
    Representa los dados de un turno.
    """

    def __init__(self, rng=None):
        """
        rng: random.Random opcional para reproducir resultados.
        """
        self.__rng__ = rng or random.Random()
        self.__valor1__ = None
        self.__valor2__ = None
        self.__tirado__ = False
        self.__restantes__ = []

    def tirar(self):
        """
        Tira los dados. Error si ya se tiró.
        """
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
        """
        Devuelve True si ambos dados son iguales.
        """
        if self.__valor1__ is None or self.__valor2__ is None:
            return False
        return self.__valor1__ == self.__valor2__

    def obtener_valores(self):
        """
        Lista de valores: [] si no se tiró, 2 valores normales o 4 si doble.
        """
        if not self.__tirado__:
            return []
        if self.es_doble():
            return [self.__valor1__] * 4  # type: ignore
        return [self.__valor1__, self.__valor2__]  # type: ignore

    def movimientos_restantes(self):
        """
        Valores que faltan consumir.
        """
        return list(self.__restantes__)

    def consumir(self, valor):
        """
        Quita una ocurrencia de 'valor'. Error si no existe o no se tiró.
        """
        if not self.__tirado__:
            raise ValueError("No se puede consumir antes de tirar.")
        try:
            self.__restantes__.remove(valor)
        except ValueError as exc:
            raise ValueError(f"El valor {valor} no está disponible.") from exc

    def quedan_movimientos(self):
        """
        True si quedan valores por usar.
        """
        return bool(self.__restantes__)

    def reiniciar_turno(self):
        """
        Limpia el estado para volver a tirar.
        """
        self.__valor1__ = None
        self.__valor2__ = None
        self.__tirado__ = False
        self.__restantes__.clear()

    def a_dict(self):
        """
        Estado serializado sencillo.
        """
        return {
            "tirado": self.__tirado__,
            "valor1": self.__valor1__,
            "valor2": self.__valor2__,
            "valores": self.obtener_valores(),
            "restantes": list(self.__restantes__),
        }

Dice = __Dice__