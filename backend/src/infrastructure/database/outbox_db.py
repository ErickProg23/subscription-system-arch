from contextlib import closing
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any


class OutboxRepository:
    """Persistencia para eventos pendientes (Outbox Pattern) en SQLite."""

    def __init__(self, db_path: str = "subscriptions.db"):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS outbox_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 5,
                    next_attempt_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def create_event(self, *, event_id: str, event_type: str, payload: str, status: str = "PENDING", max_attempts: int = 5):
        now = datetime.now(timezone.utc).isoformat()
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO outbox_events (id, event_type, payload, status, attempts, max_attempts, next_attempt_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?)
                """,
                (event_id, event_type, payload, status, max_attempts, now, now, now),
            )
            conn.commit()

    def find_ready_events(self, limit: int = 10) -> List[sqlite3.Row]:
        now = datetime.now(timezone.utc).isoformat()
        with closing(self._connect()) as conn:
            cur = conn.execute(
                """
                SELECT * FROM outbox_events
                WHERE status = 'PENDING'
                  AND (next_attempt_at IS NULL OR next_attempt_at <= ?)
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (now, limit),
            )
            rows = cur.fetchall()
        return rows

    def mark_attempt_and_reschedule(self, *, event_id: str, attempt_increment: int, backoff_seconds: int):
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        next_ts = now.timestamp() + backoff_seconds
        next_iso = datetime.fromtimestamp(next_ts, timezone.utc).isoformat()

        with closing(self._connect()) as conn:

            conn.execute(
                """
                UPDATE outbox_events
                SET attempts = attempts + ?,
                    updated_at = ?,
                    next_attempt_at = ?
                WHERE id = ?
                """,
                (attempt_increment, now_iso, next_iso, event_id),
            )
            conn.commit()

    def mark_success(self, event_id: str):
        now = datetime.now(timezone.utc).isoformat()
        with closing(self._connect()) as conn:
            conn.execute(
                """
                UPDATE outbox_events
                SET status = 'PROCESSED',
                    updated_at = ?
                WHERE id = ?
                """,
                (now, event_id),
            )
            conn.commit()

    def mark_failed(self, event_id: str):
        now = datetime.now(timezone.utc).isoformat()
        with closing(self._connect()) as conn:
            conn.execute(
                """
                UPDATE outbox_events
                SET status = 'FAILED',
                    updated_at = ?
                WHERE id = ?
                """,
                (now, event_id),
            )
            conn.commit()

