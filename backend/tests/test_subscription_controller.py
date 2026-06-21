import os
import sys
import unittest

from flask import Flask


CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from src.domain.entities.subscription import Subscription, SubscriptionStatus
from src.infrastructure.controllers.subscription_controller import create_subscription_blueprint


class DummyUseCase:
    def __init__(self, exception_message=None):
        self.exception_message = exception_message

    def execute(self, user_name, email, payment_method):
        if self.exception_message:
            raise Exception(self.exception_message)

        return Subscription(
            user_name=user_name,
            email=email,
            payment_method=payment_method,
            status=SubscriptionStatus.ACTIVE,
        )


class DummyRepository:
    def __init__(self, found_subscription=None, save_exception_message=None):
        self.found_subscription = found_subscription
        self.save_exception_message = save_exception_message

    def find_by_id(self, subscription_id):
        return self.found_subscription

    def save(self, subscription):
        if self.save_exception_message:
            raise Exception(self.save_exception_message)
        return subscription


class SubscriptionControllerTests(unittest.TestCase):
    def create_client(self, use_case=None, repository=None):
        app = Flask(__name__)
        app.register_blueprint(
            create_subscription_blueprint(
                use_case or DummyUseCase(),
                repository or DummyRepository(),
            )
        )
        return app.test_client()

    def test_subscribe_returns_400_when_body_is_invalid(self):
        client = self.create_client()

        response = client.post("/api/subscribirse", json={"user_name": "Erick"})

        self.assertEqual(response.status_code, 400)

    def test_subscribe_returns_502_when_external_service_fails(self):
        client = self.create_client(
            use_case=DummyUseCase(exception_message="500 Internal Server Error - webhook caido")
        )

        response = client.post(
            "/api/subscribirse",
            json={
                "user_name": "Erick",
                "email": "erick@example.com",
                "payment_method": {"type": "card"},
            },
        )

        self.assertEqual(response.status_code, 502)

    def test_subscribe_returns_503_when_server_error_occurs(self):
        client = self.create_client(
            use_case=DummyUseCase(exception_message="Database unavailable")
        )

        response = client.post(
            "/api/subscribirse",
            json={
                "user_name": "Erick",
                "email": "erick@example.com",
                "payment_method": {"type": "card"},
            },
        )

        self.assertEqual(response.status_code, 503)

    def test_cancel_returns_404_when_subscription_is_missing(self):
        client = self.create_client(repository=DummyRepository(found_subscription=None))

        response = client.post("/api/subscribirse/sub-404/cancelar")

        self.assertEqual(response.status_code, 404)

    def test_cancel_returns_500_when_repository_save_fails(self):
        subscription = Subscription(
            user_name="Erick",
            email="erick@example.com",
            payment_method={"type": "card"},
            status=SubscriptionStatus.ACTIVE,
        )
        client = self.create_client(
            repository=DummyRepository(
                found_subscription=subscription,
                save_exception_message="save error",
            )
        )

        response = client.post("/api/subscribirse/sub-500/cancelar")

        self.assertEqual(response.status_code, 500)

    def test_expire_returns_500_when_repository_save_fails(self):
        subscription = Subscription(
            user_name="Erick",
            email="erick@example.com",
            payment_method={"type": "card"},
            status=SubscriptionStatus.ACTIVE,
        )
        client = self.create_client(
            repository=DummyRepository(
                found_subscription=subscription,
                save_exception_message="save error",
            )
        )

        response = client.post("/api/subscribirse/sub-500/expirar")

        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
