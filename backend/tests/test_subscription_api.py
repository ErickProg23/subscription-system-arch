import json
import os
import sys
import tempfile
import unittest

from flask import Flask


CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from src.application.use_cases import CreateSubscriptionUseCase
from src.domain.entities.subscription import SubscriptionStatus
from src.infrastructure.controllers.subscription_controller import create_subscription_blueprint
from src.infrastructure.database.outbox_db import OutboxRepository
from src.infrastructure.database.sqlite_db import SqliteSubscriptionRepository


class DummyNotificationService:
    pass


class SubscriptionApiIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()
        self.db_path = temp_db.name

        self.subscription_repository = SqliteSubscriptionRepository(db_path=self.db_path)
        self.outbox_repository = OutboxRepository(db_path=self.db_path)
        self.use_case = CreateSubscriptionUseCase(
            subscription_repository=self.subscription_repository,
            notification_service=DummyNotificationService(),
            outbox_repository=self.outbox_repository,
        )

        app = Flask(__name__)
        app.register_blueprint(
            create_subscription_blueprint(self.use_case, self.subscription_repository)
        )
        self.client = app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_subscribe_creates_subscription_and_outbox_event(self):
        response = self.client.post(
            "/api/subscribirse",
            json={
                "user_name": "Erick",
                "email": "erick@example.com",
                "payment_method": {"type": "card", "last4": "4242"},
            },
        )

        self.assertEqual(response.status_code, 201)
        body = response.get_json()
        subscription_id = body["data"]["id"]

        saved_subscription = self.subscription_repository.find_by_id(subscription_id)
        ready_events = self.outbox_repository.find_ready_events()

        self.assertIsNotNone(saved_subscription)
        self.assertEqual(saved_subscription.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(len(ready_events), 1)
        self.assertEqual(
            json.loads(ready_events[0]["payload"])["subscription_id"],
            subscription_id,
        )

    def test_expire_endpoint_updates_subscription_status(self):
        create_response = self.client.post(
            "/api/subscribirse",
            json={
                "user_name": "Erick",
                "email": "erick@example.com",
                "payment_method": {"type": "card", "last4": "4242"},
            },
        )
        subscription_id = create_response.get_json()["data"]["id"]

        expire_response = self.client.post(f"/api/subscribirse/{subscription_id}/expirar")

        self.assertEqual(expire_response.status_code, 200)
        saved_subscription = self.subscription_repository.find_by_id(subscription_id)
        self.assertEqual(saved_subscription.status, SubscriptionStatus.EXPIRED)

    def test_get_subscription_returns_current_status(self):
        create_response = self.client.post(
            "/api/subscribirse",
            json={
                "user_name": "Erick",
                "email": "erick@example.com",
                "payment_method": {"type": "card", "last4": "4242"},
            },
        )
        subscription_id = create_response.get_json()["data"]["id"]

        get_response = self.client.get(f"/api/subscribirse/{subscription_id}")

        self.assertEqual(get_response.status_code, 200)
        body = get_response.get_json()
        self.assertEqual(body["data"]["id"], subscription_id)
        self.assertEqual(body["data"]["status"], "Activa")


if __name__ == "__main__":
    unittest.main()
