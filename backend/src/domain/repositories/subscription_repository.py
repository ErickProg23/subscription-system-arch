from abc import ABC, abstractmethod
from src.domain.entities.subscription import Subscription

class SubscriptionRepository(ABC):
    """Interfaz para el repositorio de suscripciones"""

    @abstractmethod
    def save(self, subscription: Subscription) -> Subscription:
        """Guarda una nueva suscripción"""
        pass

    @abstractmethod
    def find_by_id(self, subscription_id: str) -> Subscription:
        """Busca una suscripción por su ID"""
        pass