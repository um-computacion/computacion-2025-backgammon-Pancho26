from dataclasses import dataclass

@dataclass(frozen=True)
class Player:
    nombre: str
    color: str

    def __str__(self) -> str:
        return f"{self.nombre}({self.color})"