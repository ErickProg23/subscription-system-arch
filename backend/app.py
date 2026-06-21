from flask import Flask, request, jsonify, render_template
from src.infrastructure.database.sqlite_db import SqliteSubscriptionRepository
from src.infrastructure.database.outbox_db import OutboxRepository

from src.infrastructure.external_services.webhook_service import WebhookNotificationService
from src.infrastructure.workers.outbox_worker import OutboxWorker
from src.application.use_cases import CreateSubscriptionUseCase
from src.infrastructure.controllers.subscription_controller import create_subscription_blueprint


app = Flask(__name__, template_folder='templates', static_folder='static')


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


# --- 2. Registro de rutas ---
app.register_blueprint(create_subscription_blueprint(subscription_use_case, db_repository))

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
        'db_down': db_repository.simulate_db_down,
        'webhook_error': notification_service.simulate_500_error
    })

@app.route('/api/outbox/process', methods=['POST'])
def process_outbox():
    """Endpoint manual para procesar el Outbox (útil en pruebas/demos)."""
    processed = outbox_worker.process_once()
    return jsonify({"processed": processed}), 200


if __name__ == '__main__':
    print("Iniciando el servidor Flask en http://localhost:5000")
    app.run(debug=True, port =5000)


