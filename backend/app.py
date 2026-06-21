import os
import threading
import time

from flask import Flask, request, jsonify, render_template
from src.infrastructure.database.sqlite_db import SqliteSubscriptionRepository
from src.infrastructure.database.outbox_db import OutboxRepository

from src.infrastructure.external_services.webhook_service import WebhookNotificationService
from src.infrastructure.workers.outbox_worker import OutboxWorker
from src.application.use_cases import CreateSubscriptionUseCase
from src.infrastructure.controllers.subscription_controller import create_subscription_blueprint


app = Flask(__name__, template_folder='templates', static_folder='static')
WORKER_POLL_INTERVAL_SECONDS = 2


# --- 1. Configuracion de dependencias ---
db_repository = SqliteSubscriptionRepository(db_path="subscriptions.db")

notification_service = WebhookNotificationService()

outbox_repository = OutboxRepository(db_path="subscriptions.db")

subscription_use_case = CreateSubscriptionUseCase(
    subscription_repository=db_repository,
    notification_service=notification_service,
    outbox_repository=outbox_repository,
)

outbox_worker = OutboxWorker(
    outbox_repository=outbox_repository,
    webhook_service=notification_service,
)


def run_outbox_worker_forever():
    """Procesa continuamente eventos pendientes del outbox."""
    while True:
        try:
            processed = outbox_worker.process_once()
            if processed:
                print(f"[OutboxWorker] Eventos procesados: {processed}")
        except Exception as error:
            print(f"[OutboxWorker] Error procesando eventos: {error}")

        time.sleep(WORKER_POLL_INTERVAL_SECONDS)


def start_outbox_worker():
    worker_thread = threading.Thread(
        target=run_outbox_worker_forever,
        name="outbox-worker",
        daemon=True,
    )
    worker_thread.start()
    return worker_thread


# --- 2. Registro de rutas ---
app.register_blueprint(
    create_subscription_blueprint(subscription_use_case, db_repository, outbox_repository)
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate_errors', methods=['POST'])
def simulate_errors():
    data = request.get_json() or {}
    # Nota: SqliteSubscriptionRepository no implementa simulación de caída.
    # Se mantiene el endpoint por compatibilidad con la UI, pero no afecta el repositorio.

    notification_service.simulate_500_error = data.get('webhook_error', False)

    return jsonify({
        'message': 'Configuración de simulación actualizada',
        'db_down': getattr(db_repository, 'simulate_db_down', False),
        'webhook_error': notification_service.simulate_500_error
    })

@app.route('/api/outbox/process', methods=['POST'])
def process_outbox():
    """Endpoint manual para procesar el Outbox (útil en pruebas/demos)."""
    processed = outbox_worker.process_once()
    return jsonify({"processed": processed}), 200


if __name__ == '__main__':
    debug_mode = True

    if not debug_mode or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_outbox_worker()

    print("Iniciando el servidor Flask en http://localhost:5000")
    app.run(debug=debug_mode, port=5000)


