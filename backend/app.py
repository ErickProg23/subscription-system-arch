from flask import Flask, request, jsonify
from src.infrastructure.database.memory_db import MemorySubscriptionRepository
from src.infrastructure.external_services.webhook_service import WebhookNotificationService
from src.application.use_cases import CreateSubscriptionUseCase
from src.infrastructure.controllers.subscription_controller import create_subscription_blueprint

app = Flask(__name__)


# --- 1. Configuracion de dependencias ---
db_repository = MemorySubscriptionRepository()
notification_service = WebhookNotificationService()

subscription_use_case = CreateSubscriptionUseCase(
    subscription_repository=db_repository, 
    notification_service=notification_service
)

# --- 2. Registro de rutas ---
app.register_blueprint(create_subscription_blueprint(subscription_use_case))

@app.route('/api/simulate_errors', methods=['POST'])
def simulate_errors():
    data = request.get_json() or {}
    db_repository.simulate_db_down = data.get('db_down', False)
    notification_service.simulate_500_error = data.get('webhook_error', False)

    return jsonify({
        'message': 'Configuración de simulación actualizada',
        'db_down': db_repository.simulate_db_down,
        'webhook_error': notification_service.simulate_500_error
    })

if __name__ == '__main__':
    print("Iniciando el servidor Flask en http://localhost:5000")
    app.run(debug=True, port =5000)

