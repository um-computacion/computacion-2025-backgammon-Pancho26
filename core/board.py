class Board:
 
   
    def __init__(self):
        self.__posiciones__ = [[] for _ in range(24)]
        self.__barra__ = {"blanco": [], "negro": []}
        self.__fichas_fuera__ = {"blanco": [], "negro": []}
        self.inicializar_posiciones()

    def inicializar_posiciones(self):
        self.__posiciones__[0]  = ["blanco"] * 2
        self.__posiciones__[11] = ["blanco"] * 5
        self.__posiciones__[16] = ["blanco"] * 3
        self.__posiciones__[18] = ["blanco"] * 5

        self.__posiciones__[23] = ["negro"] * 2
        self.__posiciones__[12] = ["negro"] * 5
        self.__posiciones__[7]  = ["negro"] * 3
        self.__posiciones__[5]  = ["negro"] * 5
    def agregar_ficha(self, punto, color):
        self.__posiciones__[punto].append(color)

    def quitar_ficha(self, punto):
        if self.__posiciones__[punto]:
            return self.__posiciones__[punto].pop()
        return None
    def mover_ficha(self, origen, destino):
        ficha = self.quitar_ficha(origen)
        if ficha:
            destino_fichas = self.__posiciones__[destino]
            if destino_fichas and len(destino_fichas) == 1 and destino_fichas[0] != ficha:
                color_capturado = destino_fichas[0]
                self.quitar_ficha(destino)
                self.__barra__[color_capturado].append(color_capturado)
            self.agregar_ficha(destino, ficha)
    def es_movimiento_legal(self, origen, destino, color):
        if origen < 0 or origen > 23 or destino < 0 or destino > 23:
            return False
        if not self.__posiciones__[origen]:
            return False
        if self.__posiciones__[origen][-1] != color:
            return False
        destino_fichas = self.__posiciones__[destino]
        if destino_fichas and destino_fichas[0] != color and len(destino_fichas) > 1:
            return False
        if self.__barra__[color]:
            return False
        return True
 

    def puede_mover(self, color, tiradas):
        if self.__barra__[color]:
            origenes = [-1]  
        else:
            origenes = [i for i in range(24) if self.__posiciones__[i] and self.__posiciones__[i][-1] == color]
        for origen in origenes:
            for tirada in tiradas:
                if origen == -1:
                    destino = self.calcular_destino_barra(color, tirada)
                else:
                    destino = self.calcular_destino(origen, color, tirada)
                if 0 <= destino < 24 and self.es_movimiento_legal(origen if origen != -1 else destino, destino, color):
                    return True
        return False

    def calcular_destino(self, origen, color, tirada):
        if color == "blanco":
            return origen + tirada
        else:
            return origen - tirada

    def calcular_destino_barra(self, color, tirada):
        if color == "blanco":
            return tirada - 1
        else:
            return 24 - tirada

    def bornear_ficha(self, punto, color):
        ficha = self.quitar_ficha(punto)
        if ficha == color:
            self.__fichas_fuera__[color].append(ficha)