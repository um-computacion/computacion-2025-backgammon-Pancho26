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
