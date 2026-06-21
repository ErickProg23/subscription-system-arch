from src.domain.entities.subscription import Subscription, SubscriptionStatus
from src.domain.repositories.subscription_repository import SubscriptionRepository

import uuid
from datetime import datetime


class CreateSubscriptionUseCase:
    """Recibe las herramientas necesarias para ejecutar la lógica de negocio."""

    def __init__(self, subscription_repository: SubscriptionRepository, notification_service, outbox_repository):
        self.subscription_repository = subscription_repository
        self.notification_service = notification_service
        self.outbox_repository = outbox_repository

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

        # 1) Guardar la suscripción
        # (La notificación NO se hace sincrónicamente: se registra un evento en outbox)
        self.subscription_repository.save(subscription)

        # 2) Guardar evento en outbox para procesarlo async
        event_payload = {
            "subscription_id": subscription.id,
        }
        event_id = str(subscription.id)  # idempotencia simple por suscripción
        self.outbox_repository.create_event(
            event_id=event_id,
            event_type="NOTIFY_WEBHOOK",
            payload=str(event_payload),
            status="PENDING",
            max_attempts=5,
        )

        return subscription

