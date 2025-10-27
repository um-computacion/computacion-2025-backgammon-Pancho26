"""
Estado y operaciones básicas del Backgammon (independiente de UI).
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Literal


Turno = Literal["BLANCAS", "NEGRAS"]


@dataclass
class EstadoJuego:
    """
    Lleva el conteo de fichas por punto, barra, borne-off, turno y dados.

    Atributos (todos dunder):
      __blancas__, __negras__ (List[int]): Conteos por punto [0..24], se usan 1..24.
      __bar_blancas__, __bar_negras__ (int): Fichas en la barra.
      __fuera_blancas__, __fuera_negras__ (int): Fichas borne-off (0..15).
      __turno__ (Turno): "BLANCAS" o "NEGRAS".
      __dados__ (Tuple[int,int]): Última tirada.
      __movimientos_pendientes__ (List[int]): Movimientos disponibles (expande dobles).
    """

    __blancas__: List[int] = field(default_factory=lambda: [0] * 25)
    __negras__: List[int] = field(default_factory=lambda: [0] * 25)
    __bar_blancas__: int = 0
    __bar_negras__: int = 0
    __fuera_blancas__: int = 0
    __fuera_negras__: int = 0
    __turno__: Turno = "BLANCAS"
    __dados__: Tuple[int, int] = (0, 0)
    __movimientos_pendientes__: List[int] = field(default_factory=list)

    def restablecer_inicio(self) -> None:
        """
        Coloca las fichas en la posición estándar inicial.
        Retorna: None
        """
        self.__blancas__ = [0] * 25
        self.__negras__ = [0] * 25
        self.__bar_blancas__ = 0
        self.__bar_negras__ = 0
        self.__fuera_blancas__ = 0
        self.__fuera_negras__ = 0
        # Blancas: 24:2, 13:5, 8:3, 6:5
        self.__blancas__[24] = 2
        self.__blancas__[13] = 5
        self.__blancas__[8] = 3
        self.__blancas__[6] = 5
        # Negras: 1:2, 12:5, 17:3, 19:5
        self.__negras__[1] = 2
        self.__negras__[12] = 5
        self.__negras__[17] = 3
        self.__negras__[19] = 5
        self.__turno__ = "BLANCAS"
        self.__dados__ = (0, 0)
        self.__movimientos_pendientes__.clear()

    def set_dados(self, d1: int, d2: int) -> None:
        """
        Fija la tirada y genera movimientos pendientes (dobles => 4 movimientos).
        Parámetros: d1 (int), d2 (int)
        Retorna: None
        """
        if not (1 <= d1 <= 6 and 1 <= d2 <= 6):
            raise ValueError("Los dados deben estar entre 1 y 6.")
        self.__dados__ = (d1, d2)
        self.__movimientos_pendientes__ = [d1, d2] if d1 != d2 else [d1, d1, d1, d1]

    def hay_movimientos(self) -> bool:
        """
        Indica si quedan movimientos pendientes.
        Retorna: bool
        """
        return len(self.__movimientos_pendientes__) > 0

    def cambiar_turno(self) -> None:
        """
        Cambia el turno y limpia movimientos.
        Retorna: None
        """
        self.__turno__ = "NEGRAS" if self.__turno__ == "BLANCAS" else "BLANCAS"
        self.__dados__ = (0, 0)
        self.__movimientos_pendientes__.clear()

    def __dir__(self) -> int:
        """
        Dirección de avance según turno (BLANCAS: -1, NEGRAS: +1).
        Retorna: int
        """
        return -1 if self.__turno__ == "BLANCAS" else +1

    def __home_points__(self) -> range:
        """
        Rango de puntos de la casa según turno (incluye ambos extremos).
        Retorna: range
        """
        return range(1, 7) if self.__turno__ == "BLANCAS" else range(19, 25)

    def __oponente__(self) -> str:
        """
        Nombre del oponente.
        Retorna: str
        """
        return "NEGRAS" if self.__turno__ == "BLANCAS" else "BLANCAS"

    def __conteo__(self, jugador: Turno, punto: int) -> int:
        """
        Devuelve cantidad de fichas de jugador en punto.
        Parámetros: jugador (Turno), punto (int)
        Retorna: int
        """
        if not (1 <= punto <= 24):
            return 0
        return self.__blancas__[punto] if jugador == "BLANCAS" else self.__negras__[punto]

    def __set_conteo__(self, jugador: Turno, punto: int, valor: int) -> None:
        """
        Setea conteo en punto para jugador.
        Parámetros: jugador (Turno), punto (int), valor (int)
        Retorna: None
        """
        if not (1 <= punto <= 24):
            raise ValueError("Punto fuera de rango.")
        if jugador == "BLANCAS":
            self.__blancas__[punto] = valor
        else:
            self.__negras__[punto] = valor

    def __todos_en_casa__(self, jugador: Turno) -> bool:
        """
        Verifica si todas las fichas de jugador están en su casa (o fuera/barra).
        Parámetros: jugador (Turno)
        Retorna: bool
        """
        puntos_fuera = (range(7, 25) if jugador == "BLANCAS" else range(1, 19))
        arreglo = self.__blancas__ if jugador == "BLANCAS" else self.__negras__
        for p in puntos_fuera:
            if arreglo[p] > 0:
                return False
        return True

    def __punto_mas_lejano_en_casa__(self, jugador: Turno) -> Optional[int]:
        """
        Punto propio en casa más lejano a la salida (para overshoot).
        Parámetros: jugador (Turno)
        Retorna: Optional[int]
        """
        puntos = (range(6, 0, -1) if jugador == "BLANCAS" else range(19, 25))
        arreglo = self.__blancas__ if jugador == "BLANCAS" else self.__negras__
        for p in puntos:
            if arreglo[p] > 0:
                return p
        return None

    def puede_mover(self, desde: int, pasos: int) -> bool:
        """
        Valida si puede mover desde un punto usando 'pasos'.
        Parámetros: desde (int), pasos (int)
        Retorna: bool
        """
        if pasos not in self.__movimientos_pendientes__:
            return False
        if not (1 <= desde <= 24):
            return False
        jugador = self.__turno__
        oponente = self.__oponente__()
        if self.__conteo__(jugador, desde) <= 0:
            return False

        direccion = self.__dir__()
        hasta = desde + direccion * pasos

        # Movimiento dentro del tablero
        if 1 <= hasta <= 24:
            # Bloqueado si hay 2+ fichas del oponente
            if self.__conteo__(oponente, hasta) >= 2:
                return False
            return True

        # Intento de borne-off
        if not self.__todos_en_casa__(jugador):
            return False
        # Exacto o overshoot permitido desde el punto más lejano
        punto_lejano = self.__punto_mas_lejano_en_casa__(jugador)
        if punto_lejano is None:
            return False
        # Distancia exacta al fuera
        if jugador == "BLANCAS":
            # salir por 0
            if hasta < 1:
                return (desde == pasos) or (desde == punto_lejano and desde < pasos)
        else:
            # salir por 25
            if hasta > 24:
                dist = 25 - desde
                return (dist == pasos) or (desde == punto_lejano and dist < pasos)
        return False

    def mover(self, desde: int, pasos: int) -> None:
        """
        Ejecuta el movimiento (captura y borne-off incluidos).
        Parámetros: desde (int), pasos (int)
        Retorna: None
        """
        if not self.puede_mover(desde, pasos):
            raise ValueError("Movimiento inválido.")

        jugador = self.__turno__
        oponente = self.__oponente__()
        direccion = self.__dir__()
        hasta = desde + direccion * pasos

        # Salida del punto origen
        self.__set_conteo__(jugador, desde, self.__conteo__(jugador, desde) - 1)

        # Dentro del tablero: aplicar captura si hay blote
        if 1 <= hasta <= 24:
            if self.__conteo__(oponente, hasta) == 1:
                # Captura
                self.__set_conteo__(oponente, hasta, 0)
                if oponente == "BLANCAS":
                    self.__bar_blancas__ += 1
                else:
                    self.__bar_negras__ += 1
            # Colocar ficha
            self.__set_conteo__(jugador, hasta, self.__conteo__(jugador, hasta) + 1)
        else:
            # Borne-off
            if jugador == "BLANCAS":
                self.__fuera_blancas__ += 1
            else:
                self.__fuera_negras__ += 1

        # Consumir dado usado
        self.__movimientos_pendientes__.remove(pasos)
        if not self.hay_movimientos():
            self.cambiar_turno()

    def puede_reingresar(self, pasos: int) -> bool:
        """
        Valida reingreso desde barra con 'pasos'.
        Parámetros: pasos (int)
        Retorna: bool
        """
        if pasos not in self.__movimientos_pendientes__:
            return False
        jugador = self.__turno__
        oponente = self.__oponente__()
        if jugador == "BLANCAS":
            if self.__bar_blancas__ <= 0:
                return False
            destino = 25 - pasos  # 24..19
        else:
            if self.__bar_negras__ <= 0:
                return False
            destino = pasos  # 1..6
        if not (1 <= destino <= 24):
            return False
        # Bloqueado si hay 2+ del oponente
        if self.__conteo__(oponente, destino) >= 2:
            return False
        return True

    def reingresar(self, pasos: int) -> None:
        """
        Reingresa una ficha desde la barra usando 'pasos'.
        Parámetros: pasos (int)
        Retorna: None
        """
        if not self.puede_reingresar(pasos):
            raise ValueError("Reingreso inválido.")

        jugador = self.__turno__
        oponente = self.__oponente__()
        destino = (25 - pasos) if jugador == "BLANCAS" else pasos

        # Bajar de la barra
        if jugador == "BLANCAS":
            self.__bar_blancas__ -= 1
        else:
            self.__bar_negras__ -= 1

        # Captura si hay blote
        if self.__conteo__(oponente, destino) == 1:
            self.__set_conteo__(oponente, destino, 0)
            if oponente == "BLANCAS":
                self.__bar_blancas__ += 1
            else:
                self.__bar_negras__ += 1

        # Colocar ficha
        self.__set_conteo__(jugador, destino, self.__conteo__(jugador, destino) + 1)

        # Consumir movimiento
        self.__movimientos_pendientes__.remove(pasos)
        if not self.hay_movimientos():
            self.cambiar_turno()