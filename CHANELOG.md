# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
- Test que cubran el codigo
- El archivo __init__.py en la carpeta test

### Changed
- Renombrados atributos de la clase `Board` para cumplir con la consigna de doble guion bajo.

### Removed
- Eliminación de duplicados en métodos de verificación de movimiento legal.
