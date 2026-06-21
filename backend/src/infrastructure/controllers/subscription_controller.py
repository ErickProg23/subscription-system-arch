from flask import Blueprint, request, jsonify
from src.domain.entities.subscription import SubscriptionStatus


def create_subscription_blueprint(use_case, repository, outbox_repository):
    "Creamos uin Blueprint de Flask para manejar las rutas relacionadas con las suscripciones"
    ""
    subscription_bp = Blueprint("subscriptions", __name__)

    @subscription_bp.route('/api/subscribirse/<sub_id>', methods=['GET'])
    def get_subscription(sub_id):
        try:
            suscripcion = repository.find_by_id(sub_id)

            if not suscripcion:
                return jsonify({"error": "Suscripción no encontrada"}), 404

            return jsonify({
                "message": "Suscripción consultada exitosamente",
                "data": suscripcion.to_dict()
            }), 200
        except Exception as e:
            return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500

    @subscription_bp.route('/api/subscribirse/<sub_id>/payment-status', methods=['GET'])
    def get_payment_status(sub_id):
        try:
            event = outbox_repository.find_event_by_id(sub_id)

            if not event:
                return jsonify({
                    "message": "Aun no existe confirmación de pago para esta suscripción",
                    "payment_status": "PENDING",
                }), 200

            status_map = {
                "PENDING": "PENDING",
                "PROCESSED": "CONFIRMED",
                "FAILED": "FAILED",
            }

            return jsonify({
                "message": "Estado de notificación consultado exitosamente",
                "payment_status": status_map.get(event["status"], "PENDING"),
                "attempts": event["attempts"],
            }), 200
        except Exception as e:
            return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500

    def update_subscription_status(sub_id, new_status):
        suscripcion = repository.find_by_id(sub_id)

        if not suscripcion:
            return jsonify({"error": "Suscripción no encontrada"}), 404

        suscripcion.status = new_status
        repository.save(suscripcion)

        return jsonify({
            "message": f"Suscripción {new_status.value.lower()} exitosamente",
            "status": suscripcion.status.value
        }), 200
    
    @subscription_bp.route('/api/subscribirse', methods=['POST'])
    def subscribe():
        data = request.get_json()

        # Validamos que se haya proporcionado los datos de entrada
        if not data or 'user_name' not in data or 'email' not in data or 'payment_method' not in data:
            return jsonify({"error": "Faltan datos requeridos (user_name, email, payment_method)"}), 400
        
        try:

            subscription = use_case.execute(
                user_name=data['user_name'],
                email=data['email'],
                payment_method=data['payment_method']
            )

            return jsonify({
                "message": "Suscripcion creada exitosamente",
                "data": subscription.to_dict()
            }), 201
        
        
        except Exception as e:
            error_message = str(e)

            # Mantener compatibilidad con la interfaz original.
            # Con SQLite/BD real podemos mapear cualquier excepción a 503 (DB) o 502 (externo)
            # dependiendo del origen del error.
            if "500" in error_message or "servicio externo" in error_message.lower() or "webhook" in error_message.lower():
                return jsonify({"error": "Fallo en el servicio de pagos externo", "details": error_message}), 502

            # Por defecto asumimos problemas de BD como 503
            return jsonify({"error": "Fallo en el servidor", "details": error_message}), 503


    # --- NUEVA RUTA PARA CANCELAR ---
    @subscription_bp.route('/api/subscribirse/<sub_id>/cancelar', methods=['POST'])
    def cancelar(sub_id):
        try:
            return update_subscription_status(sub_id, SubscriptionStatus.CANCELED)
        except Exception as e:
            return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500

    @subscription_bp.route('/api/subscribirse/<sub_id>/expirar', methods=['POST'])
    def expirar(sub_id):
        try:
            return update_subscription_status(sub_id, SubscriptionStatus.EXPIRED)
        except Exception as e:
            return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500

    return subscription_bp
