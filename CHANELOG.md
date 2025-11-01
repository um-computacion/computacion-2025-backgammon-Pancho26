

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
