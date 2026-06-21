from flask import Blueprint, request, jsonify
from src.domain.entities.subscription import SubscriptionStatus

def create_subscription_blueprint(use_case, repository):
    "Creamos uin Blueprint de Flask para manejar las rutas relacionadas con las suscripciones"
    ""
    subscription_bp = Blueprint("subscriptions", __name__)
    
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
            
            # Verificamos si es un error de conexión
            if "conexión" in error_message.lower():
                return jsonify({"error": "Fallo en la base de datos", "details": error_message}), 503
            
            # Verificamos si es un error de servidor externo (500)
            elif "500" in error_message:
                return jsonify({"error": "Fallo en el servicio de pagos externo", "details": error_message}), 502
            
            # Cualquier otra cosa
            else:
                return jsonify({"error": "Error interno del servidor", "details": error_message}), 500
        pass

    # --- NUEVA RUTA PARA CANCELAR ---
    @subscription_bp.route('/api/subscribirse/<sub_id>/cancelar', methods=['POST'])
    def cancelar(sub_id):
        try:
            # 1. Buscamos la suscripción en memoria
            suscripcion = repository.find_by_id(sub_id)
            
            if not suscripcion:
                return jsonify({"error": "Suscripción no encontrada"}), 404
            
            # 2. Cambiamos el estado
            suscripcion.status = SubscriptionStatus.CANCELED
            
            # 3. Guardamos el cambio (en memoria es automático si modificas el objeto, 
            # pero es buena práctica llamar al save)
            repository.save(suscripcion)
            
            return jsonify({
                "message": "Suscripción cancelada exitosamente",
                "status": suscripcion.status.value
            }), 200
            
        except Exception as e:
            return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500

    return subscription_bp
