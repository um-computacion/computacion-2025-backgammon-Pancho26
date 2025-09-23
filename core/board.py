BLANCO = "blanco"
NEGRO = "negro"

class Board:
    """
    Representa el tablero de Backgammon con 24 puntos, barra y fichas fuera.
    """

    def __init__(self):
        """
        Inicializa el tablero, la barra y las fichas fuera. Coloca las fichas en posiciones estándar.
        """
        self.__posiciones__ = [[] for _ in range(24)]
        self.__barra__ = {BLANCO: [], NEGRO: []}
        self.__fichas_fuera__ = {BLANCO: [], NEGRO: []}
        self.inicializar_posiciones()

    def inicializar_posiciones(self):
        # Blancas
        self.__posiciones__[0]  = [BLANCO] * 2
        self.__posiciones__[11] = [BLANCO] * 5
        self.__posiciones__[16] = [BLANCO] * 3
        self.__posiciones__[18] = [BLANCO] * 5
        # Negras
        self.__posiciones__[23] = [NEGRO] * 2
        self.__posiciones__[12] = [NEGRO] * 5
        self.__posiciones__[7]  = [NEGRO] * 3
        self.__posiciones__[5]  = [NEGRO] * 5

    def agregar_ficha(self, punto, color):
        """Agrega una ficha del color indicado al punto dado."""
        self.__posiciones__[punto].append(color)

    def quitar_ficha(self, punto):
        """Quita y devuelve la ficha superior del punto o None si está vacío."""
        if self.__posiciones__[punto]:
            return self.__posiciones__[punto].pop()
        return None

    def mover_ficha(self, origen, destino):
        """Mueve una ficha del origen al destino manejando capturas si corresponde."""
        ficha = self.quitar_ficha(origen)
        if not ficha:
            return
        destino_fichas = self.__posiciones__[destino]
      
        if destino_fichas and len(destino_fichas) == 1 and destino_fichas[0] != ficha:
            capturado = self.__posiciones__[destino].pop()
            self.__barra__[capturado].append(capturado)
        self.agregar_ficha(destino, ficha)

    def es_movimiento_legal(self, origen, destino, color):
        """Verifica si el movimiento propuesto es legal para el color dado."""
        if destino < 0 or destino > 23:
            return False

        
        if self.__barra__[color] and origen != -1:
            return False

       
        if origen == -1:
            destino_fichas = self.__posiciones__[destino]
            
            if destino_fichas and destino_fichas[0] != color and len(destino_fichas) > 1:
                return False
            return True

        
        if origen < 0 or origen > 23:
            return False
        if not self.__posiciones__[origen]:
            return False
        if self.__posiciones__[origen][-1] != color:
            return False

        destino_fichas = self.__posiciones__[destino]
       
        if destino_fichas and destino_fichas[0] != color and len(destino_fichas) > 1:
            return False

        return True

    def puede_mover(self, color, tiradas):
        """Indica si el jugador puede realizar algún movimiento con las tiradas dadas."""
        
        if self.__barra__[color]:
            origenes = [-1]
        else:
            origenes = [
                i for i in range(24)
                if self.__posiciones__[i] and self.__posiciones__[i][-1] == color
            ]

        for origen in origenes:
            for tirada in tiradas:
                destino = self.calcular_destino_barra(color, tirada) if origen == -1 else self.calcular_destino(origen, color, tirada)
                if 0 <= destino < 24 and self.es_movimiento_legal(origen, destino, color):
                    return True
        return False

    def calcular_destino(self, origen, color, tirada):
        if color == BLANCO:
            return origen + tirada
        else:
            return origen - tirada

    def calcular_destino_barra(self, color, tirada):
        if color == BLANCO:
            return tirada - 1
        else:
            return 24 - tirada

    def bornear_ficha(self, punto, color):
        ficha = self.quitar_ficha(punto)
        if ficha == color:
            self.__fichas_fuera__[color].append(ficha)

    def todos_en_casa(self, color):
        """Devuelve True si todas las fichas del color están en su tablero interno y no hay en la barra."""
        if self.__barra__[color]:
            return False
        if color == BLANCO:
            for i, pila in enumerate(self.__posiciones__):
                if any(f == BLANCO for f in pila) and not (18 <= i <= 23):
                    return False
        else:
            for i, pila in enumerate(self.__posiciones__):
                if any(f == NEGRO for f in pila) and not (0 <= i <= 5):
                    return False
        return True

    def puede_bornear(self, origen, color, tirada):
        """Valida si se puede bornear desde 'origen' con la 'tirada' dada."""
        if origen < 0 or origen > 23:
            return False
        if not self.__posiciones__[origen] or self.__posiciones__[origen][-1] != color:
            return False
        if not self.todos_en_casa(color):
            return False

        if color == BLANCO:
            destino = origen + tirada
            if destino == 24:
                return True
            if destino > 23:
                # Overroll: permitido solo si no hay blancas en puntos mayores a 'origen'
                for i in range(origen + 1, 24):
                    if any(f == BLANCO for f in self.__posiciones__[i]):
                        return False
                return True
            return False
        else:
            destino = origen - tirada
            if destino == -1:
                return True
            if destino < 0:
                # Overroll: permitido solo si no hay negras en puntos menores a 'origen'
                for i in range(0, origen):
                    if any(f == NEGRO for f in self.__posiciones__[i]):
                        return False
                return True
            return False

    def bornear_si_valido(self, origen, color, tirada):
        """Borneo si es legal según la tirada y devuelve True si se realizó."""
        if not self.puede_bornear(origen, color, tirada):
            return False
        ficha = self.quitar_ficha(origen)
        if ficha == color:
            self.__fichas_fuera__[color].append(ficha)
            return True
        if ficha is not None:
            self.agregar_ficha(origen, ficha)
        return False

    def contar_en_barra(self, color):
        """Devuelve la cantidad de fichas del color en la barra."""
        return len(self.__barra__[color])

    def ha_ganado(self, color):
        """Indica si el jugador ya borneó sus 15 fichas."""
        return len(self.__fichas_fuera__[color]) >= 15

    def obtener_estado_puntos(self):
        estado = []
        for pila in self.__posiciones__:
            if pila:
                estado.append({"color": pila[0], "cantidad": len(pila)})
            else:
                estado.append({"color": None, "cantidad": 0})
        return estado

    def obtener_punto(self, indice):
        return list(self.__posiciones__[indice])

    def obtener_barra(self, color=None):
        if color is None:
            return {c: list(p) for c, p in self.__barra__.items()}
        return list(self.__barra__[color])

    def obtener_fuera(self, color=None):
        if color is None:
            return {c: list(p) for c, p in self.__fichas_fuera__.items()}
        return list(self.__fichas_fuera__[color])

    def mover_desde_barra(self, color, destino):
        """Mueve una ficha desde la barra al destino si el movimiento es válido."""
        if not self.__barra__[color]:
            return False
        destino_fichas = self.__posiciones__[destino]
        
        if destino_fichas and destino_fichas[0] != color and len(destino_fichas) > 1:
            return False
        
        self.__barra__[color].pop()
        
        if destino_fichas and len(destino_fichas) == 1 and destino_fichas[0] != color:
            capturado = self.__posiciones__[destino].pop()
            self.__barra__[capturado].append(capturado)
       
        self.__posiciones__[destino].append(color)
        return True

    def aplicar_movimiento(self, origen, destino, color):
        """Aplica un movimiento desde el origen (o barra) hacia el destino."""
        if origen == -1:
            return self.mover_desde_barra(color, destino)
        self.mover_ficha(origen, destino)
        return True