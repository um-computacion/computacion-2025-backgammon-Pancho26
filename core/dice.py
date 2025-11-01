"""Dice implementation for a Backgammon turn (supports doubles and consumption)."""
import random

class __Dice__:  # pylint: disable=invalid-name
    """Dados de un turno: tirar, consultar valores/movimientos y consumir."""

    def __init__(self, rng=None):
        """Inicializa con RNG opcional (random.Random compatible)."""
        self.__rng__ = rng or random.Random()
        self.__valor1__ = None
        self.__valor2__ = None
        self.__tirado__ = False
        self.__restantes__ = []

    def tirar(self):
        """Tira los dados; si es doble, genera 4 movimientos."""
        if self.__tirado__:
            raise ValueError("Los dados ya fueron tirados este turno.")
        self.__valor1__ = self.__rng__.randint(1, 6)
        self.__valor2__ = self.__rng__.randint(1, 6)
        self.__tirado__ = True
        self.__restantes__ = (
            [self.__valor1__] * 4 if self.es_doble() else [self.__valor1__, self.__valor2__]
        )

    def es_doble(self):
        """True si ambos dados muestran el mismo valor."""
        if self.__valor1__ is None or self.__valor2__ is None:
            return False
        return self.__valor1__ == self.__valor2__

    def obtener_valores(self):
        """Devuelve la lista de valores del turno (4 si es doble)."""
        if not self.__tirado__:
            return []
        # dividir la línea para cumplir longitud máxima
        if self.es_doble():
            return [self.__valor1__] * 4  # type: ignore
        return [self.__valor1__, self.__valor2__]  # type: ignore

    def movimientos_restantes(self):
        """Copia de los movimientos aún disponibles."""
        return list(self.__restantes__)

    def consumir(self, valor):
        """Consume una aparición de 'valor' de los movimientos restantes."""
        if not self.__tirado__:
            raise ValueError("No se puede consumir antes de tirar.")
        try:
            self.__restantes__.remove(valor)
        except ValueError as exc:
            raise ValueError(f"El valor {valor} no está disponible.") from exc

    def quedan_movimientos(self):
        """True si quedan movimientos por consumir."""
        return bool(self.__restantes__)

    def reiniciar_turno(self):
        """Limpia estado interno para un nuevo turno."""
        self.__valor1__ = None
        self.__valor2__ = None
        self.__tirado__ = False
        self.__restantes__.clear()

    def a_dict(self):
        """Serializa el estado actual del dado."""
        return {
            "tirado": self.__tirado__,
            "valor1": self.__valor1__,
            "valor2": self.__valor2__,
            "valores": self.obtener_valores(),
            "restantes": list(self.__restantes__),
        }

    def tirado(self):
        """True si ya se tiraron los dados en el turno."""
        return self.__tirado__

    def puede_consumir(self, valor):
        """True si 'valor' está disponible para consumir."""
        return valor in self.__restantes__

    def valor_maximo(self):
        """Valor máximo disponible o None si no hay."""
        return max(self.__restantes__) if self.__restantes__ else None

Dice = __Dice__