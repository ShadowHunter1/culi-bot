import sqlite3
import hashlib
import time
from pathlib import Path
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS alert_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_hash  TEXT NOT NULL,
    alertname   TEXT NOT NULL,
    namespace   TEXT,
    severity    TEXT,
    raw_text    TEXT,
    ai_response TEXT,
    message_id  INTEGER,
    created_at  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dedup_counter (
    alert_hash  TEXT PRIMARY KEY,
    count       INTEGER DEFAULT 1,
    first_seen  INTEGER NOT NULL,
    last_seen   INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_alert_hash ON alert_history(alert_hash);
CREATE INDEX IF NOT EXISTS idx_created_at ON alert_history(created_at);
"""

RETENTION_DAYS = 30

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init(self):
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    def make_hash(self, alertname: str, namespace: str) -> str:
        key = f"{alertname}|{namespace}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def is_duplicate(self, alert_hash: str, cooldown_seconds: int = 1800) -> bool:
        """Chỉ CHECK, không update counter."""
        now = int(time.time())
        with self._conn() as conn:
            row = conn.execute(
                "SELECT last_seen FROM dedup_counter WHERE alert_hash = ?",
                (alert_hash,)
            ).fetchone()
            return bool(row and (now - row["last_seen"]) < cooldown_seconds)

    def mark_processed(self, alert_hash: str):
        """Chỉ update counter SAU KHI xử lý thành công."""
        now = int(time.time())
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO dedup_counter (alert_hash, count, first_seen, last_seen)
                   VALUES (?, 1, ?, ?)
                   ON CONFLICT(alert_hash) DO UPDATE SET
                   count = count + 1, last_seen = excluded.last_seen""",
                (alert_hash, now, now)
            )

    def save_alert(self, alert_hash, alertname, namespace, severity, raw_text, ai_response, message_id):
        now = int(time.time())
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO alert_history
                   (alert_hash, alertname, namespace, severity, raw_text, ai_response, message_id, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (alert_hash, alertname, namespace, severity, raw_text, ai_response, message_id, now)
            )

    def get_stats(self) -> dict:
        cutoff = int(time.time()) - RETENTION_DAYS * 86400
        with self._conn() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM alert_history WHERE created_at > ?", (cutoff,)
            ).fetchone()[0]
            by_name = conn.execute(
                """SELECT alertname, COUNT(*) as cnt FROM alert_history
                   WHERE created_at > ? GROUP BY alertname ORDER BY cnt DESC LIMIT 10""",
                (cutoff,)
            ).fetchall()
        return {"total": total, "top_alerts": [dict(r) for r in by_name]}

    def get_recent(self, limit: int = 5) -> list:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT alertname, namespace, severity, created_at
                   FROM alert_history ORDER BY created_at DESC LIMIT ?""",
                (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def cleanup_old(self):
        cutoff = int(time.time()) - RETENTION_DAYS * 86400
        with self._conn() as conn:
            conn.execute("DELETE FROM alert_history WHERE created_at < ?", (cutoff,))