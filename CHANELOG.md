

# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.1] - 2025-11-01
### Changed
- Ajustes finales y mejoras en la suite de tests para estabilizar la integración continua.

## [0.7.0] - 2025-10-27
### Added
- Tablero gráfico completo en `ui/` con controlador Pygame (`ControladorUI`), geometría, temas y detección de puntas.
- Botones de tirar y sacar fichas, cálculo de pasos y manejo de victorias en la UI.
- Hooks entre `cli.app` y la UI para propagar preferencias y estado del juego.
### Changed
- Refinamientos al loop de Pygame, redimensionado y selección de movimientos para mejorar la usabilidad.

## [0.6.0] - 2025-10-22
### Added
- Configuración de Pylint (`.pylintrc`) y pruebas dedicadas para CLI, player y checker.
- Integración inicial de Pygame: helpers de render ASCII en `cli.main`, adapters de tablero y helpers de estado/barras.
- Nuevos tests de integración para CLI cubriendo flags, renderización y compatibilidad.
### Changed
- Ajustes en CLI y estado para soportar auto-skip configurable, render de dados y compatibilidad con distintas APIs de `Game`.

## [0.5.0] - 2025-10-14
### Added
- Clase `core.game.Game` que orquesta turnos, adaptadores de tablero y consumo de dados.
- Nuevas reglas y documentación de gameplay, incluyendo prompts y notas de reglas.
- Pruebas unitarias para dados, tablero y game cubriendo reglas de borne-off, dobles y movimientos no legales.
### Changed
- Ajustes de reglas y validaciones identificadas en `core/board.py` y `core/dice.py`.
- Mantenimiento del changelog y correcciones menores en documentación.
### Fixed
- Bugs reportados en el flujo de juego y validaciones de movimientos.

## [0.4.0] - 2025-10-01
### Added
- Paquete `cli` con `cli.app` y `cli.state` como interfaz principal para lanzar la aplicación.
- Estado de juego reutilizable (`EstadoJuego`) con inicialización estándar de fichas, turnos y movimientos pendientes.
- Entrypoint de línea de comandos con flags para tamaño de ventana, FPS y opciones de tiradas.
### Changed
- Reorganización de `core.player` y `core.checker` para integrarse con el CLI.

## [0.3.0] - 2025-09-30
### Added
- Nuevos helpers y funciones en `core.board` y `core.dice` para completar reglas pendientes y preparar la integración con la UI.
- Suite de pruebas ampliada para `board`, `dice` y `checker`, incluyendo coberturas adicionales y fixtures.
- Integración de cobertura automatizada, SonarCloud y reportes generados vía GitHub Actions (`.github/workflows/ci.yml`, `.coveragerc`, `coverage.xml`).
### Changed
- Refactor de `Board` y `Dice` siguiendo principios SOLID, simplificando responsabilidades y mejorando legibilidad.
- Ajustes de cobertura y estilos para alinearlos con los nuevos pipelines de calidad.
### Fixed
- Correcciones puntuales en validaciones de `board` detectadas por las nuevas pruebas.

## [0.2.0] - 2025-09-15
### Added
- Clase `__Dice__` (alias `Dice`) para gestionar tiradas de dados.
- Métodos: `tirar`, `es_doble`, `obtener_valores`, `movimientos_restantes`,
  `consumir`, `quedan_movimientos`, `reiniciar_turno`, `a_dict`.
- Tests unitarios para estados iniciales, dobles, consumo, reinicio, determinismo y serialización.
- Docstrings completos en `core/dice.py`.
- Archivo de documentación `docs/dice.md`.

### Changed
- Ajuste de `obtener_valores()` para retornar [] si no se tiró y soportar lógica de tests que inspeccionan directamente atributos.
- Estructura de valores restantes centralizada en `__restantes__`.

### Fixed
- Manejo de error al intentar tirar más de una vez en el mismo turno.
- Validación de consumo antes de tirar.

## [0.1.0] - 2025-09-07
### Added
- Estructura inicial del proyecto y carpetas principales.
- Clase `Board` con atributos para posiciones, barra y fichas fuera.
- Método para inicializar posiciones estándar del tablero.
- Métodos para agregar y quitar fichas en el tablero.
- Método para mover fichas entre puntos.
- Lógica de captura de fichas (enviar a la barra).
- Método para verificar si un movimiento es legal.
- Métodos para calcular destino de movimientos y reingreso desde la barra.
- Método para verificar si el jugador puede mover.
- Método para bornear fichas (sacar del tablero).
- Test que cubran el código.
- El archivo __init__.py en la carpeta test.

### Changed
- Renombrados atributos de la clase `Board` para cumplir con la consigna de doble guion bajo.

### Removed
- Eliminación de duplicados en métodos de verificación de movimiento legal.
