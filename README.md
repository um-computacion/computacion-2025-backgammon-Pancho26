# Backgammon 2025

Proyecto educativo de Backgammon para dos jugadores con interfaz en Pygame.

## Requisitos

- Python 3.10 o superior
- Pygame 2.x
- (Opcional) requirements.txt con dependencias del proyecto

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/Pancho26/computacion-2025-backgammon.git
   cd computacion-2025-backgammon
   ```
2. (Recomendado) Crear entorno virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt  # o al menos: pip install pygame
   ```

## Ejecución rápida (Pygame)

Desde la raíz del proyecto:
```bash
python cli/app.py
```

Parámetros opcionales:
- Dimensiones y FPS:
  - `--ancho 1000`
  - `--alto 700`
  - `--fps 60`
- Reglas de turno:
  - `--saltear-sin-movimientos` habilita que, si un jugador no tiene movimientos legales, se pase automáticamente el turno (por defecto ON).
  - `--no-saltear-sin-movimientos` desactiva ese comportamiento.
- Visualización de dados (para evitar que queden tapados por fichas):
  - `--dados-encima` dibuja los dados por encima de las fichas (por defecto ON).
  - `--dados-debajo` dibuja los dados por debajo de las fichas.
  - `--dados-posicion {top|bottom}` elige si los dados se muestran arriba o abajo del tablero.
  - `--dados-offset-y <px>` ajuste fino vertical en píxeles (por defecto 16).

Ejemplos:
```bash
# Ventana estándar y pasar turno si no hay movimientos
python cli/app.py --ancho 1000 --alto 700 --fps 60 --saltear-sin-movimientos

# Poner los dados arriba, por encima de las fichas, con un pequeño desplazamiento
python cli/app.py --dados-encima --dados-posicion top --dados-offset-y 16
```

Notas:
- También puedes controlar estas preferencias vía variables de entorno:
  - `BACKGAMMON_AUTO_SKIP_NO_MOVES=1|0`
  - `BACKGAMMON_DICE_DRAW_ON_TOP=1|0`
  - `BACKGAMMON_DICE_POSITION=top|bottom`
  - `BACKGAMMON_DICE_Y_OFFSET=<px>`

## Estructura (resumen)

- `cli/app.py`: punto de entrada de la app (Pygame y CLI).
- `cli/state.py`: estado y configuración del juego.
- `ui/controller.py`: controlador de la interfaz Pygame.

## Objetivo

Explorar las reglas y estrategias del Backgammon y practicar conceptos de programación y arquitectura de software.

