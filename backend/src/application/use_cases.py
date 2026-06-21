from src.domain.entities.subscription import Subscription, SubscriptionStatus
from src.domain.repositories.subscription_repository import SubscriptionRepository

class CreateSubscriptionUseCase:
    """ Recibe las herramientas necesarias para ejecutar la lógica de negocio relacionada con las suscripciones. """

    def __init__(self, subscription_repository: SubscriptionRepository, notification_service):
        self.subscription_repository = subscription_repository
        self.notification_service = notification_service


    def execute(self, user_name: str, email: str, payment_method: dict) -> Subscription:
        """ Crea una nueva suscripción para un usuario. """

        # Validar los datos de entrada
        if not user_name or not email or not payment_method:
            raise ValueError("Todos los campos son obligatorios.")

        # Crear la suscripción
        subscription = Subscription(
            user_name=user_name,
            email=email,
            payment_method=payment_method,
            status=SubscriptionStatus.ACTIVE
        )

        # Guardar la suscripcion en la base de datos
        # (Si la DB falla, el codigo se detiene y nunca se cobra ni notifica al usuario)
        self.subscription_repository.save(subscription)

        # Enviar una notificación al usuario
        self.notification_service.notify_payment_success(subscription.id)

        return subscription