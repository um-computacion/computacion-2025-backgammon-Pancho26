# Justificación General del Proyecto

## 1. Resumen del diseño general
El proyecto se estructura en capas separadas: `core/` concentra la lógica pura de Backgammon (tablero, dados, jugadores y orquestación de turnos); `cli/` expone un modo de ejecución sin UI gráfica (estado serializable y entrada por línea de comandos); `ui/` implementa la experiencia en Pygame; `test/` valida cada módulo con PyTest. La comunicación entre capas se realiza mediante adaptadores y contratos (Protocols) que permiten ejecutar la lógica central sin depender de la interfaz elegida.

## 2. Justificación de las clases elegidas
- **core.board.Board**: encapsula el estado completo del tablero, barra y borne-off. Provee utilidades de validación, movimiento y compatibilidad con la API histórica del curso.
- **core.dice.Dice** (`__Dice__`): administra tiradas, dobles y consumo de movimientos. Mantiene el estado del turno y expone serialización para depuración.
- **core.game.Game**: orquesta turnos, delega en `BoardAdapter` y `MovementRule` y aplica el principio de inversión de dependencias; evita mezclar UI con lógica.
- **core.game.BoardAdapter**: traduce la API en español del tablero (`es_movimiento_legal`, `aplicar_movimiento`) a un contrato estable (`BoardPort`).
- **core.game.MovementRule** y `BasicMovementRule`: permiten intercambiar estrategias de selección de dados sin tocar la clase principal.
- **core.player.Player**: representa al jugador, valida el color y ofrece helpers de movimiento reutilizando la lógica del board.
- **cli.state.EstadoJuego**: mantiene un estado simple para CLI/Pygame (conteos, turnos, dados pendientes) y actúa como capa anticorrupción hacia la UI.
- **cli.app.Aplicacion**: configura flags, estado y variables de entorno antes de lanzar la UI o la CLI.
- **ui.controller.ControladorUI** junto a `ui.geometry`, `ui.render`, `ui.theme`: encapsulan la interacción con Pygame, renderizado, botones y detección de puntas.
- **test/\***: cubre board, dice, player, game y CLI para garantizar que las clases anteriores funcionen juntas.

## 3. Justificación de atributos
- **Doble guion bajo**: se utilizan alias `__posiciones__`, `__barra__`, `__fichas_fuera__` en `Board` para cumplir la consigna y mantener compatibilidad con los tests iniciales. `EstadoJuego` emplea sistemáticamente `__blancas__`, `__negras__`, `__dados__`, etc., facilitando inspección desde la UI y validando el requisito de nomenclatura.
- **Atributos protegidos (`_points`, `_bar`, `_borne_off`)** en `Board`: simplifican operaciones internas pero se mantienen expuestos vía alias dunder para el enunciado.
- **`EstadoJuego.__movimientos_pendientes__`**: almacena tiradas expandidas (manejo de dobles) para que la UI y la CLI puedan consumirlas sin depender de `core.dice`.
- **`ControladorUI.__btn_tirar__`, `__btn_sacar__`, `__seleccion_origen__`**: agrupan estado visual y de interacción del tablero, aislando la lógica de input.
- **Variables de entorno (`BACKGAMMON_*`)**: permiten coordinar preferencias entre CLI y UI sin acoplar clases.

## 4. Decisiones de diseño relevantes
- Separación estricta entre lógica (`core`) y presentación (`cli`/`ui`) para cumplir con la requisito de accesibilidad en entornos sin interfaz gráfica.
- Uso de Protocols (`DicePort`, `BoardPort`, `MovementRule`) en `core.game` para facilitar el testing aislado y la sustitución de componentes.
- Adaptadores y helpers en `cli.main` que generan representaciones ASCII o consultas al tablero real, permitiendo reutilizar la lógica central.
- Integración de Pygame con botones, detección de hover y reglas de victoria dentro del controlador sin contaminar `EstadoJuego`.
- Automatización de calidad: pipeline de CI con coverage y SonarCloud, generación de reportes y configuración de Pylint.
- Gestión de configuración por argumento en CLI y traspaso a UI por medio de `EstadoJuego`, evitando duplicación de lógica.

## 5. Excepciones y manejo de errores
- `core.dice.Dice` valida secuencia de uso y levanta `ValueError` cuando se intenta tirar dos veces o consumir valores inexistentes.
- `Board` usa métodos `*_require_*` (checks de color y punto) que levantan `ValueError` para garantizar integridad del tablero.
- `Game.BoardAdapter` atrapa excepciones comunes (`RuntimeError`, `ValueError`, `AttributeError`, `TypeError`) para no quebrar el flujo y reportar movimientos inválidos.
- `Player.mover` y `Player.bornear` protegen la interacción con el tablero con `try/except` devolviendo `False` ante fallas.
- La UI verifica estados (`__ganador__`, `hay_movimientos`) antes de aceptar acciones para evitar inconsistencias.

## 6. Estrategias de testing y cobertura
- `test_board.py` y `test_checker.py` validan reglas básicas del tablero y fichas.
- `test_dice.py` cubre tiradas, dobles, consumo y serialización del dado.
- `test_game.py` asegura el flujo de turnos, consumo de dados y bloqueos de movimientos.
- `test_cli.py` valida parsing de flags, helpers ASCII y contratos con la UI.
- `pytest` es la herramienta principal de orquestación; la configuración de cobertura se centraliza en `.coveragerc` y `coverage.xml`.
- El workflow de GitHub Actions ejecuta tests, genera reportes, ejecuta Pylint y publica resultados para mantener la cobertura monitoreada.

## 7. Referencias a principios SOLID
- **S (Single Responsibility)**: `Board` mantiene estado y reglas; `Dice` sólo gestiona tiradas; `Game` orquesta turnos; `ControladorUI` se centra en eventos/render.
- **O (Open/Closed)**: `MovementRule` permite nuevas políticas sin modificar `Game`; la UI admite nuevos temas/diseños extendiendo clases auxiliares.
- **L (Liskov Substitution)**: cualquier objeto que implemente `DicePort` o `BoardPort` puede reemplazar las implementaciones por defecto (usado en tests con dobles).
- **I (Interface Segregation)**: se proveen contratos específicos pequeños (p. ej., `MovementRule` sólo define dos métodos).
- **D (Dependency Inversion)**: `Game` recibe adaptadores y dados por constructor; `Aplicacion` inyecta `EstadoJuego` en la UI en lugar de que la UI lo cree.

## 8. Anexos
```
BackgammonGame
├─ BoardAdapter ─► Board
├─ Dice (DicePort)
├─ MovementRule
└─ Player

CLI
├─ Aplicacion
└─ EstadoJuego

UI (Pygame)
├─ ControladorUI
├─ RenderizadorTablero / TemaTablero
└─ MotorDisposicion / DeteccionPuntas
```
*(Pendiente de trasladar a diagrama UML formal; el esquema anterior resume dependencias actuales.)*
