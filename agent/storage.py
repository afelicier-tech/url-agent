# storage.py
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional
from config import settings

# Simple SQLite for local dev
class SQLiteStorage:
    def __init__(self, path="url_checks.db"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._ensure_table()

    def _ensure_table(self):
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS url_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            final_url TEXT,
            status_code INTEGER,
            ok INTEGER,
            redirects INTEGER,
            latency_ms INTEGER,
            content_type TEXT,
            headers TEXT,
            body_snippet TEXT,
            error TEXT,
            created_at TEXT
        )
        """)
        self.conn.commit()

    def insert(self, record: Dict[str, Any]):
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO url_checks (url, final_url, status_code, ok, redirects, latency_ms, content_type, headers, body_snippet, error, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.get("url"),
            record.get("final_url"),
            record.get("status_code"),
            1 if record.get("ok") else 0,
            record.get("redirects_count", 0),
            record.get("latency_ms"),
            record.get("content_type"),
            json.dumps(record.get("headers", {}))[:2000],
            (record.get("body") or "")[:1000],
            record.get("error"),
            datetime.utcnow().isoformat()
        ))
        self.conn.commit()


def get_storage():
	return SQLiteStorage()
