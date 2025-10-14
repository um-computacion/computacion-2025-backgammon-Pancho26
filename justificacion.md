# Justificación de diseño y principios SOLID

Resumen:
- Se aislaron responsabilidades: Board (estado y reglas básicas), Dice (tiradas y consumo), Game (orquestación), BoardAdapter (traducción de API), MovementRule (estrategia de selección/validación de dados), Player (valor objeto).
- Se redujo acoplamiento y duplicación en core/game.py.

S — Single Responsibility
- Board: administra puntos, barra, borne-off y validaciones básicas (bloqueos).
- Dice: estado y consumo de tiradas (incluye dobles).
- Game: flujo de turnos, consumo de dados y delegación de movimientos.
- BoardAdapter: adapta la API de Board a un contrato neutro para Game (no mezcla lógica de turnos).
- Player: solo identificación de jugador.

O — Open/Closed
- MovementRule permite cambiar la política para seleccionar el dado (p. ej., reglas forzadas) sin modificar Game.
- BoardAdapter permite cambiar Board sin modificar Game.

L — Liskov Substitution
- DicePort/BoardPort son contratos (Protocol). Cualquier implementación compatible los puede sustituir (p. ej., fakes en tests).

I — Interface Segregation
- Protocols pequeños y específicos (DicePort, BoardPort, MovementRule). No obligan a implementar métodos no usados.

D — Dependency Inversion
- Game depende de abstracciones (DicePort, BoardPort, MovementRule) e inyecta dependencias por constructor.
- Board concreto se usa vía BoardAdapter.

Notas de consistencia
- Unificación de colores usando BLANCO/NEGRO de Board en Game para evitar errores de mapeo.
- Cálculo de pasos en el adaptador incluye casos desde barra (origen == -1).
- Se eliminaron duplicaciones y código muerto en core/game.py.

Implicancias en tests
- No se modificó Board ni Dice para preservar pruebas existentes.
- Game queda listo para tests unitarios aislados creando dobles (fakes) que cumplan los Protocols.
