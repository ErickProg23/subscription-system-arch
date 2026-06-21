import uuid
from datetime import datetime
from enum import Enum

# 1. Definimos las reglas estrictas de los estados
class SubscriptionStatus(Enum):
    ACTIVE = "Activa"
    CANCELED = "Cancelada"
    EXPIRED = "Esxpirada"

#2. Creamos el molde de nuestra suscripción
class Subscription:
    def __init__(self, user_name: str, email: str, payment_method: str, status: SubscriptionStatus = SubscriptionStatus.ACTIVE):
        self.id = str(uuid.uuid4())  # Generamos un ID único para cada suscripción
        self.user_name = user_name
        self.email = email
        self.payment_method = payment_method
        self.status = status
        self.created_at = datetime.now()

    def to_dict(self):
        """Convertimos la suscripción a un diccionario para facilitar su almacenamiento o transmisión"""
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
            "payment_method": self.payment_method,
            "status": self.status.value,  # Guardamos el valor del enum
            "created_at": self.created_at.isoformat()
        }