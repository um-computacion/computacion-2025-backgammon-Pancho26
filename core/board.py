class Board:
   
    def __init__(self):
        self.__puntos__ = [[] for _ in range(24)]
        self.__barra__ = {"blanco": [], "negro": []}
        self.__fichas_fuera__ = {"blanco": [], "negro": []}