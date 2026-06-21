import json
import os
import sys
import unittest


CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from src.infrastructure.workers.outbox_worker import OutboxWorker


class FakeOutboxRepository:
    def __init__(self, events):
        self.events = events
        self.success_ids = []
        self.failed_ids = []
        self.rescheduled = []

    def find_ready_events(self, limit=10):
        return self.events[:limit]

    def mark_success(self, event_id):
        self.success_ids.append(event_id)

    def mark_failed(self, event_id):
        self.failed_ids.append(event_id)

    def mark_attempt_and_reschedule(self, **kwargs):
        self.rescheduled.append(kwargs)


class FakeWebhookService:
    def __init__(self, result=True):
        self.result = result
        self.called_with = []

    def notify_payment_success(self, subscription_id):
        self.called_with.append(subscription_id)
        return self.result


class OutboxWorkerTests(unittest.TestCase):
    def test_marks_event_as_processed_when_webhook_succeeds(self):
        repository = FakeOutboxRepository(
            [
                {
                    "id": "event-1",
                    "event_type": "NOTIFY_WEBHOOK",
                    "payload": json.dumps({"subscription_id": "sub-1"}),
                    "attempts": 0,
                    "max_attempts": 5,
                }
            ]
        )
        webhook_service = FakeWebhookService(result=True)
        worker = OutboxWorker(
            outbox_repository=repository,
            webhook_service=webhook_service,
        )

        processed = worker.process_once()

        self.assertEqual(processed, 1)
        self.assertEqual(webhook_service.called_with, ["sub-1"])
        self.assertEqual(repository.success_ids, ["event-1"])
        self.assertEqual(repository.failed_ids, [])
        self.assertEqual(repository.rescheduled, [])

    def test_reschedules_event_when_webhook_fails_temporarily(self):
        repository = FakeOutboxRepository(
            [
                {
                    "id": "event-2",
                    "event_type": "NOTIFY_WEBHOOK",
                    "payload": json.dumps({"subscription_id": "sub-2"}),
                    "attempts": 1,
                    "max_attempts": 5,
                }
            ]
        )
        webhook_service = FakeWebhookService(result=False)
        worker = OutboxWorker(
            outbox_repository=repository,
            webhook_service=webhook_service,
        )

        processed = worker.process_once()

        self.assertEqual(processed, 1)
        self.assertEqual(repository.success_ids, [])
        self.assertEqual(repository.failed_ids, [])
        self.assertEqual(len(repository.rescheduled), 1)
        self.assertEqual(repository.rescheduled[0]["event_id"], "event-2")
        self.assertEqual(repository.rescheduled[0]["backoff_seconds"], 4)

    def test_marks_event_as_failed_when_payload_is_invalid(self):
        repository = FakeOutboxRepository(
            [
                {
                    "id": "event-3",
                    "event_type": "NOTIFY_WEBHOOK",
                    "payload": json.dumps({}),
                    "attempts": 4,
                    "max_attempts": 5,
                }
            ]
        )
        webhook_service = FakeWebhookService(result=True)
        worker = OutboxWorker(
            outbox_repository=repository,
            webhook_service=webhook_service,
        )

        processed = worker.process_once()

        self.assertEqual(processed, 1)
        self.assertEqual(repository.failed_ids, ["event-3"])
        self.assertEqual(webhook_service.called_with, [])


if __name__ == "__main__":
    unittest.main()
