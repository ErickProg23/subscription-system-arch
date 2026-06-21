import os
import sys
import unittest
from unittest.mock import patch


CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from src.infrastructure.external_services.webhook_service import WebhookNotificationService


class WebhookNotificationServiceTests(unittest.TestCase):
    @patch("src.infrastructure.external_services.webhook_service.time.sleep", return_value=None)
    def test_returns_true_when_notification_succeeds(self, _mock_sleep):
        service = WebhookNotificationService()

        result = service.notify_payment_success("sub-1")

        self.assertTrue(result)

    @patch("src.infrastructure.external_services.webhook_service.time.sleep", return_value=None)
    def test_returns_false_after_exhausting_retries(self, _mock_sleep):
        service = WebhookNotificationService()
        service.simulate_500_error = True

        result = service.notify_payment_success("sub-2")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
