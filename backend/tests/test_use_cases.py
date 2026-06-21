import json
import os
import sys
import unittest


CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from src.application.use_cases import CreateSubscriptionUseCase
from src.domain.entities.subscription import SubscriptionStatus


class InMemorySubscriptionRepository:
    def __init__(self):
        self.saved_subscription = None

    def save(self, subscription):
        self.saved_subscription = subscription
        return subscription


class InMemoryOutboxRepository:
    def __init__(self):
        self.events = []

    def create_event(self, **kwargs):
        self.events.append(kwargs)


class DummyNotificationService:
    pass


class CreateSubscriptionUseCaseTests(unittest.TestCase):
    def test_creates_active_subscription_and_json_outbox_event(self):
        subscription_repository = InMemorySubscriptionRepository()
        outbox_repository = InMemoryOutboxRepository()
        use_case = CreateSubscriptionUseCase(
            subscription_repository=subscription_repository,
            notification_service=DummyNotificationService(),
            outbox_repository=outbox_repository,
        )

        subscription = use_case.execute(
            user_name="Erick",
            email="erick@example.com",
            payment_method={"type": "card", "last4": "4242"},
        )

        self.assertIsNotNone(subscription_repository.saved_subscription)
        self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(len(outbox_repository.events), 1)
        self.assertEqual(outbox_repository.events[0]["event_id"], subscription.id)

        payload = json.loads(outbox_repository.events[0]["payload"])
        self.assertEqual(payload["subscription_id"], subscription.id)

    def test_raises_error_when_required_fields_are_missing(self):
        use_case = CreateSubscriptionUseCase(
            subscription_repository=InMemorySubscriptionRepository(),
            notification_service=DummyNotificationService(),
            outbox_repository=InMemoryOutboxRepository(),
        )

        with self.assertRaises(ValueError):
            use_case.execute("", "erick@example.com", {"type": "card"})


if __name__ == "__main__":
    unittest.main()
