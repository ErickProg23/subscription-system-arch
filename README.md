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
- un test de integracion para el flujo HTTP con Flask + SQLite

Para ejecutarlos:

```powershell
cd backend
python -m unittest discover -s tests -v
```

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

## Limitaciones Conocidas

- SQLite es suficiente para demo, no para alta concurrencia real
- la operacion `guardar suscripcion + guardar evento outbox` aun puede mejorarse con una transaccion unica
- el servicio externo esta simulado, no integrado con un proveedor real

## Proximos Pasos

- aumentar cobertura de tests
- agregar Docker
- agregar CI/CD
- hacer transaccional la escritura de suscripcion y outbox
- migrar a una cola real para produccion
