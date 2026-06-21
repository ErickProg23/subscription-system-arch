# Prueba Tecnica - Sistema de Suscripciones

## Resumen

Este repositorio contiene una solucion backend para una prueba tecnica de suscripciones.
El objetivo es exponer una API para registrar suscripciones, persistir su estado, notificar
un servicio externo simulado cuando el pago es exitoso y aplicar resiliencia ante fallos del
servicio externo mediante reintentos.

La implementacion actual utiliza:

- Python
- Flask
- SQLite
- Arquitectura por capas inspirada en Clean Architecture / Hexagonal
- Outbox Pattern para desacoplar la integracion externa

## Requerimientos Cubiertos

### 1. API

Se expone un endpoint para crear suscripciones:

- `POST /api/subscribirse`

Recibe:

```json
{
  "user_name": "Erick",
  "email": "erick@example.com",
  "payment_method": {
    "type": "card",
    "last4": "4242"
  }
}
```

### 2. Persistencia

La suscripcion se guarda en SQLite con los estados de negocio:

- `Activa`
- `Cancelada`
- `Expirada`

Endpoints adicionales:

- `POST /api/subscribirse/<id>/cancelar`
- `POST /api/subscribirse/<id>/expirar`

### 3. Integracion

Cuando una suscripcion se crea, el sistema registra un evento en una tabla `outbox_events`.
Ese evento luego es procesado por un worker en segundo plano que notifica al servicio externo
simulado.

### 4. Resiliencia

Si la notificacion falla, el evento no se pierde. El worker vuelve a intentar con backoff
exponencial hasta alcanzar el numero maximo de intentos configurado.

## Arquitectura

El proyecto esta separado en capas para aislar responsabilidades:

### Dominio

Ubicacion: `backend/src/domain`

- Define la entidad `Subscription`
- Define el enum `SubscriptionStatus`
- Define el contrato `SubscriptionRepository`

La capa de dominio no conoce Flask, SQLite ni detalles de infraestructura.

### Aplicacion

Ubicacion: `backend/src/application`

- Contiene el caso de uso `CreateSubscriptionUseCase`
- Coordina la creacion de la suscripcion y la publicacion del evento en outbox

Aqui vive la logica del proceso de negocio.

### Infraestructura

Ubicacion: `backend/src/infrastructure`

- `controllers/`: endpoints HTTP con Flask
- `database/`: implementaciones concretas de persistencia
- `external_services/`: simulacion del webhook externo
- `workers/`: procesamiento del outbox

Esta capa contiene lo tecnico: base de datos, framework web e integraciones.

## Estructura Principal

```text
backend/
  app.py
  requirements.txt
  src/
    application/
      use_cases.py
    domain/
      entities/
        subscription.py
      repositories/
        subscription_repository.py
    infrastructure/
      controllers/
        subscription_controller.py
      database/
        sqlite_db.py
        outbox_db.py
      external_services/
        webhook_service.py
      workers/
        outbox_worker.py
  tests/
    test_use_cases.py
    test_outbox_worker.py
    test_subscription_api.py
```

## Como Ejecutar El Proyecto

### 1. Crear entorno virtual

En Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar dependencias

```powershell
cd backend
pip install -r requirements.txt
```

### 3. Ejecutar la aplicacion

```powershell
python app.py
```

La aplicacion quedara disponible en:

- `http://localhost:5000`

## Endpoints Disponibles

### Crear suscripcion

```http
POST /api/subscribirse
```

### Cancelar suscripcion

```http
POST /api/subscribirse/<id>/cancelar
```

### Expirar suscripcion

```http
POST /api/subscribirse/<id>/expirar
```

### Simular error del webhook

```http
POST /api/simulate_errors
```

Body:

```json
{
  "webhook_error": true
}
```

### Procesar manualmente el outbox

```http
POST /api/outbox/process
```

Nota: existe para pruebas y demo. En la implementacion actual tambien hay un worker automatico
que procesa eventos pendientes en segundo plano.

## Tests

Se incluyeron:

- tests unitarios del caso de uso
- tests unitarios del worker de outbox
- tests del controller para cubrir flujos exitosos y de error
- tests del servicio de webhook
- un test de integracion para el flujo HTTP con Flask + SQLite

Para ejecutarlos:

```powershell
cd backend
python -m unittest discover -s tests -v
```

Para medir cobertura:

```powershell
cd backend
coverage erase
coverage run --source=src -m unittest discover -s tests -v
coverage report -m
```

Cobertura actual del backend medida sobre `src`: `87%`.

## Decisiones Tecnicas

### Por que separar en capas

La separacion permite:

- cambiar SQLite por PostgreSQL sin tocar el dominio
- cambiar Flask por FastAPI sin rehacer la logica de negocio
- probar la logica sin depender de HTTP ni de una base de datos real

### Por que usar outbox

Si la notificacion al servicio externo se hiciera dentro del request HTTP:

- la respuesta al cliente seria mas lenta
- un fallo externo bloquearia la operacion
- aumentaria el acoplamiento entre la API y el servicio externo

Con outbox:

- primero se persiste el evento
- luego un worker lo procesa
- si falla, se reintenta sin perder la intencion de notificar

### Manejo de errores

- errores de validacion responden con `400`
- errores inesperados del servidor responden con `5xx`
- errores del webhook se intentan mitigar con retry

### Justificacion de la transaccion de base de datos

El flujo actual guarda primero la suscripcion y luego registra el evento en outbox.
Para la prueba tecnica priorice una solucion simple, legible y funcional que demostrara:

- persistencia del estado de suscripcion
- desacoplamiento con el servicio externo
- resiliencia con retry y outbox

En este punto, si la base de datos cayera exactamente entre la escritura de la suscripcion y
la escritura del evento del outbox, podria existir una inconsistencia temporal: la suscripcion
quedaria almacenada pero el evento no.

Esta decision fue consciente para mantener el alcance acotado de la prueba y enfocarme en
mostrar la separacion de capas, el flujo de negocio y la resiliencia ante fallos del servicio
externo.

En un entorno de produccion, la mejora natural seria encapsular `guardar suscripcion + guardar
evento outbox` dentro de una unica transaccion de base de datos usando una sola conexion y
`commit/rollback` atomico. De esa forma:

- si ambas operaciones salen bien, se confirma la transaccion
- si una falla, se revierte todo
- se evita dejar suscripciones persistidas sin su evento de notificacion asociado

Por lo tanto, para esta prueba la estrategia adoptada demuestra el patron y el flujo completo,
pero reconozco explicitamente que la version ideal de produccion debe hacer esa escritura de
forma transaccional.

## Escalabilidad En Produccion

Si el sistema recibiera 10,000 suscripciones por segundo, la evolucion natural seria:

### 1. Base de datos mas robusta

- migrar de SQLite a PostgreSQL o MySQL
- usar indices y particionamiento si el volumen crece

### 2. Cola de mensajeria

En lugar de procesar el outbox en un hilo local, se podria:

- publicar eventos a RabbitMQ o Kafka
- tener multiples consumidores procesando pagos/notificaciones
- escalar horizontalmente los workers

### 3. API stateless

- ejecutar varias instancias del backend detras de un balanceador
- compartir la base de datos y la cola

### 4. Observabilidad

- logs estructurados
- metricas de intentos, fallos y latencia
- alertas cuando la cola crezca o el webhook falle repetidamente

## Docker y CI/CD En Produccion

Como parte del README de la prueba, la propuesta para llevar este backend a produccion seria:

### Docker

- crear un `Dockerfile` para empaquetar la API con sus dependencias
- usar variables de entorno para configuracion sensible
- ejecutar la aplicacion en un contenedor desacoplado del host

### CI/CD

- ejecutar tests y cobertura en cada push o pull request
- bloquear merges si falla la suite o si la cobertura cae por debajo del minimo esperado
- construir la imagen Docker automaticamente tras validar la rama principal
- desplegar a un entorno de staging o produccion de forma controlada

## Limitaciones Conocidas

- SQLite es suficiente para demo, no para alta concurrencia real
- la operacion `guardar suscripcion + guardar evento outbox` debe hacerse con una transaccion unica en produccion
- el servicio externo esta simulado, no integrado con un proveedor real

## Proximos Pasos

- agregar Docker
- agregar CI/CD
- hacer transaccional la escritura de suscripcion y outbox
- migrar a una cola real para produccion
