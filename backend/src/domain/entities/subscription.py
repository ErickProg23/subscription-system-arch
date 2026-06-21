import uuid
from datetime import datetime
from enum import Enum

# 1. Definimos las reglas estrictas de los estados
class SubscriptionStatus(Enum):
    ACTIVE = "Activa"
    CANCELED = "Cancelada"
    EXPIRED = "Expirada"

#2. Creamos el molde de nuestra suscripción
class Subscription:
    # Añadimos 'id: str = None' al final de los parámetros
    def __init__(self, user_name: str, email: str, payment_method: str, status: SubscriptionStatus = SubscriptionStatus.ACTIVE, id: str = None):
        # Si viene un id, lo usamos. Si no, generamos uno nuevo.
        self.id = id if id else str(uuid.uuid4())  
        self.user_name = user_name
        self.email = email
        self.payment_method = payment_method
        self.status = status
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
            "payment_method": self.payment_method,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }