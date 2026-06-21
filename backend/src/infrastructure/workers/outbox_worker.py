import json
from typing import Optional

from src.infrastructure.database.outbox_db import OutboxRepository
from src.infrastructure.external_services.webhook_service import WebhookNotificationService


class OutboxWorker:
    """Worker que procesa eventos pendientes del Outbox."""

    def __init__(
        self,
        *,
        outbox_repository: OutboxRepository,
        webhook_service: WebhookNotificationService,
        batch_size: int = 10,
    ):
        self.outbox_repository = outbox_repository
        self.webhook_service = webhook_service
        self.batch_size = batch_size

    def process_once(self) -> int:
        ready_events = self.outbox_repository.find_ready_events(limit=self.batch_size)
        processed = 0

        for ev in ready_events:
            ev_id = ev["id"]
            event_type = ev["event_type"]
            payload_raw = ev["payload"]
            attempts = ev["attempts"]
            max_attempts = ev["max_attempts"]

            if event_type != "NOTIFY_WEBHOOK":
                self.outbox_repository.mark_failed(ev_id)
                processed += 1
                continue

            try:
                payload = json.loads(payload_raw)
                subscription_id = payload.get("subscription_id")

                if not subscription_id:
                    self.outbox_repository.mark_failed(ev_id)
                    processed += 1
                    continue

                ok = self.webhook_service.notify_payment_success(subscription_id)
                if ok:
                    self.outbox_repository.mark_success(ev_id)
                    processed += 1
                else:
                    if attempts + 1 >= max_attempts:
                        self.outbox_repository.mark_failed(ev_id)
                    else:
                        backoff_seconds = 2 ** (attempts + 1)
                        self.outbox_repository.mark_attempt_and_reschedule(
                            event_id=ev_id,
                            attempt_increment=1,
                            backoff_seconds=backoff_seconds,
                        )
                    processed += 1

            except Exception:
                if attempts + 1 >= max_attempts:
                    self.outbox_repository.mark_failed(ev_id)
                else:
                    backoff_seconds = 2 ** (attempts + 1)
                    self.outbox_repository.mark_attempt_and_reschedule(
                        event_id=ev_id,
                        attempt_increment=1,
                        backoff_seconds=backoff_seconds,
                    )
                processed += 1

        return processed

