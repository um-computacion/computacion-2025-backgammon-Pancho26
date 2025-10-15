from core import BLANCO, NEGRO
from core.player import Player
from core.game import Game

def main() -> int:
    blanco = Player("Blancas", BLANCO)
    negro = Player("Negras", NEGRO)
    game = Game(blanco, negro)

    print("Backgammon CLI")
    print("Comandos: tablero, barra, fuera, tirar, mover, mover_barra, turno, pasar, reset, salir")

    while True:
        ganador = game.ganador()
        if ganador:
            print(f"¡Ganó {ganador}!")
            return 0

        try:
            linea = input(f"[{game.turno}] ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not linea:
            continue

        parts = linea.split()
        cmd, *args = parts
        cmd = cmd.lower()

        if cmd in ("salir", "exit", "quit"):
            break
        elif cmd == "tablero":
            print(game.tablero_compacto())
        elif cmd == "barra":
            print(game.estado_barras())
        elif cmd == "fuera":
            print(game.estado_fuera())
        elif cmd == "turno":
            print(f"Turno: {game.turno} | Tiradas: {game.tiradas or '-'}")
        elif cmd == "reset":
            game.reset()
            print("Partida reiniciada.")
        elif cmd == "tirar":
            if game.tiradas:
                print(f"Ya hay tiradas: {game.tiradas}")
            else:
                d1, d2 = game.tirar_dados()
                print(f"Dados: {d1}, {d2} -> tiradas: {game.tiradas}")
                if not game.puede_mover(game.turno):
                    print("Sin movimientos. Se pasa el turno.")
                    game.fin_de_turno_si_corresponde()
        elif cmd == "mover":
            if len(args) != 2:
                print("Uso: mover <origen> <destino> (origen=-1 para barra)")
                continue
            try:
                origen = int(args[0])
                destino = int(args[1])
            except ValueError:
                print("Origen y destino deben ser enteros.")
                continue
            if not game.tiradas:
                print("Primero tirá los dados con 'tirar'.")
                continue
            if game.mover(game.turno, origen, destino):
                print("OK.")
                print(game.tablero_compacto())
                if game.fin_de_turno_si_corresponde():
                    print(f"Turno de {game.turno}.")
                else:
                    print(f"Tiradas restantes: {game.tiradas}")
            else:
                print("Movimiento inválido (bloqueo o no coincide con dados).")
        elif cmd == "mover_barra":
            if len(args) != 1:
                print("Uso: mover_barra <destino>")
                continue
            try:
                destino = int(args[0])
            except ValueError:
                print("Destino debe ser entero.")
                continue
            if not game.tiradas:
                print("Primero tirá los dados con 'tirar'.")
                continue
            if game.mover(game.turno, -1, destino):
                print("OK.")
                print(game.tablero_compacto())
                if game.fin_de_turno_si_corresponde():
                    print(f"Turno de {game.turno}.")
                else:
                    print(f"Tiradas restantes: {game.tiradas}")
            else:
                print("No se pudo reingresar (bloqueo o no coincide con dados).")
        elif cmd == "pasar":
            if game.tiradas and game.puede_mover(game.turno):
                print("Aún hay movimientos posibles; no se puede pasar.")
            else:
                game.fin_de_turno_si_corresponde()
                print(f"Turno de {game.turno}.")
        else:
            print("Comando desconocido.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())