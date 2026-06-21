# Frontend - Sistema de Suscripciones

## Resumen

Este frontend fue construido con `React + TypeScript + Vite` para consumir la API de suscripciones
del backend. Su objetivo es ofrecer una experiencia clara y mantenible para:

- crear una suscripción
- validar datos en cliente
- visualizar el estado real de la suscripción
- confirmar el pago inicial mediante polling al backend
- manejar estados de carga, éxito, error, timeout y fallo de red

## Stack Tecnológico

- React 18
- TypeScript
- Vite
- Vitest
- Testing Library
- Playwright

## Requerimientos Cubiertos

### Interfaz de usuario

- formulario de suscripción con validación de nombre, email y método de pago simulado
- dashboard para visualizar estados `Activa`, `Cancelada` y `Expirada`
- notificación de confirmación del pago inicial basada en el estado real del backend

### Integración con backend

- consumo de endpoints mediante un cliente HTTP reutilizable
- manejo de carga, éxito y error
- reintentos automáticos con timeout y clasificación de errores

### UX/UI

- feedback visual durante el proceso de pago
- mensajes claros para errores de validación, servidor, timeout y red
- layout responsive para escritorio y móvil

## Estructura de Carpetas

```text
frontend/
  src/
    components/
      AlertMessage.tsx
      NotificationToast.tsx
      SubscriptionDashboard.tsx
      SubscriptionForm.tsx
    hooks/
      usePaymentConfirmation.ts
    services/
      apiClient.ts
      subscriptionService.ts
    test/
      setup.ts
    tests/
      e2e/
        subscription-flow.spec.ts
    types/
      subscription.ts
    utils/
      validation.ts
    App.tsx
    main.tsx
    styles.css
  playwright.config.ts
  index.html
  package.json
  tsconfig.json
  vite.config.ts
```

## Arquitectura Frontend

El frontend se separó por responsabilidades para cumplir mejor con el criterio evaluado:

### Presentación

Ubicación: `src/components`

- componentes visuales reutilizables
- formularios, mensajes, dashboard y toast

### Lógica de negocio

Ubicación: `src/hooks` y `src/utils`

- polling para confirmación del pago
- validación client-side del formulario

### Servicios

Ubicación: `src/services`

- `apiClient.ts`: encapsula `fetch`, timeout, retries y clasificación de errores
- `subscriptionService.ts`: centraliza el acceso a los endpoints del backend

### Tipos

Ubicación: `src/types`

- contratos TypeScript para payloads, respuestas y estados

## Flujo Principal

1. El usuario completa el formulario de suscripción.
2. El frontend valida datos antes de enviar.
3. Se llama al endpoint `POST /api/subscribirse`.
4. Si la creación es exitosa, se muestra el dashboard con los datos persistidos.
5. El hook `usePaymentConfirmation` consulta periódicamente el estado del pago inicial.
6. Cuando el backend confirma el pago, se actualiza la interfaz y se muestra una notificación.

## Comunicación con el Backend

El frontend consume estos endpoints:

- `POST /api/subscribirse`
- `GET /api/subscribirse/:id`
- `GET /api/subscribirse/:id/payment-status`
- `POST /api/subscribirse/:id/cancelar`
- `POST /api/subscribirse/:id/expirar`

En desarrollo, Vite usa un proxy hacia `http://localhost:5000` definido en `vite.config.ts`.

## Cómo Ejecutarlo

### 1. Instalar dependencias

```powershell
cd frontend
npm install
```

### 2. Levantar el frontend

```powershell
npm run dev
```

La aplicación quedará disponible normalmente en:

- `http://localhost:5173`

### 3. Backend requerido

Para que el frontend funcione correctamente, el backend Flask debe estar levantado en:

- `http://localhost:5000`

## Tests

### Ejecutar tests unitarios

```powershell
cd frontend
npm run test
```

### Medir cobertura

```powershell
cd frontend
npm run coverage
```

Cobertura actual del frontend: `84.19%`.

### Instalar navegadores para E2E

```powershell
cd frontend
npm run playwright:install
```

### Ejecutar tests E2E

```powershell
cd frontend
npm run test:e2e
```

### Ejecutar tests E2E en modo visual

```powershell
cd frontend
npm run test:e2e:ui
```

Estado actual de E2E: `1 flujo principal aprobado con Playwright`.

## Decisiones Técnicas

### Por qué React + TypeScript

- permite separar responsabilidades de forma clara
- mejora mantenibilidad y escalabilidad del código
- TypeScript ayuda a definir contratos fuertes entre frontend y backend

### Por qué una capa de servicios

En lugar de llamar `fetch` directamente desde los componentes:

- se centralizó la comunicación HTTP
- se reutilizó la lógica de timeout y reintentos
- se separó la vista de los detalles de infraestructura

### Por qué polling para confirmar el pago

Para esta prueba técnica se eligió polling como una solución simple y suficiente para:

- consultar el estado real del pago inicial
- evitar mostrar éxito antes de tiempo
- demostrar integración real con el backend

En producción, una evolución natural sería usar WebSocket o Server-Sent Events.

## Manejo de Errores

El frontend diferencia entre:

- errores de validación
- errores del servidor
- errores de red
- timeouts

Esto permite dar mensajes más claros al usuario y mejorar la UX.

## Performance

Las decisiones actuales priorizan claridad y mantenibilidad para la prueba técnica. Aun así:

- se evita lógica HTTP duplicada con una capa de servicios
- el dashboard se actualiza solo cuando cambian acciones relevantes
- la validación se resuelve en cliente antes del envío

Mejoras naturales para una siguiente iteración:

- debouncing en validaciones o búsquedas futuras
- lazy loading de pantallas si el frontend crece
- code splitting por rutas o módulos

## Limitaciones Conocidas

- aún no se implementa lazy loading
- la confirmación del pago usa polling en lugar de WebSocket
- `main.tsx` y algunos archivos de tipos no aportan demasiado a la cobertura, aunque el total global sí supera el mínimo requerido
- actualmente se cubre el flujo principal E2E, pero aún no existen escenarios E2E adicionales para errores, expiración y reintentos de red

## Próximos Pasos

- documentar diagrama de componentes y comunicación con backend
- ampliar la cobertura E2E para cancelación, expiración y fallos controlados
- incorporar lazy loading si el proyecto crece
- limpiar por completo la interfaz legacy incrustada en Flask cuando el frontend React quede como único cliente oficial
