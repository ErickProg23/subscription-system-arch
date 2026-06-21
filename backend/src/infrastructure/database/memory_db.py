from src.domain.entities.subscription import Subscription
from src.domain.repositories.subscription_repository import SubscriptionRepository

class MemorySubscriptionRepository(SubscriptionRepository):
    """ Implementacion real del contrato En lugar de una base de datos, se utiliza una lista en memoria para almacenar las suscripciones. """
    def __init__(self):
        self._subscriptions = {}
        self.simulate_db_down = False

    def save(self, subscription: Subscription) -> None:
        # Aqqui se responde la pregunta en el caso de que se caiga la BD se lanza un error antes de guadar la suscripcion
        if self.simulate_db_down:
            raise Exception("Error: Se perdio la conexión a la base de datos.")
        
        self._subscriptions[subscription.id] = subscription.to_dict()

    def find_by_id(self, subscription_id: str) -> Subscription:
        # Busca la suscripción por ID en la lista de suscripciones
        sub_data = self._subscriptions.get(subscription_id)

        if not sub_data:
            raise Exception("Error: Suscripción no encontrada.")
        return None
    
        # si la encuentra, la devulve a armar como una entidad
        return Subscription(
            user_name=sub_data['user_name'],
            email=sub_data['email'],
            payment_method=sub_data['payment_method'],
            status=sub_data['status'],
            id=sub_data['id']
        )