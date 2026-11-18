"""Local SQLite persistence for interview sessions."""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

BASE_DIR = Path(__file__).resolve().parent.parent


class SessionStore:
    def __init__(self, database_path: Optional[Path] = None):
        configured_path = os.environ.get("INTERVIEW_DB_PATH")
        self.database_path = Path(database_path or configured_path or BASE_DIR / "data" / "interviews.sqlite3")
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.database_path, timeout=5.0)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS interview_sessions (
                    session_id TEXT PRIMARY KEY,
                    candidate_name TEXT NOT NULL,
                    persona_name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    question_count INTEGER NOT NULL,
                    session_json TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _validate_id(session_id: str) -> str:
        try:
            return str(UUID(session_id))
        except (ValueError, AttributeError) as exc:
            raise ValueError("Invalid interview session ID.") from exc

    def save(
        self,
        session_id: str,
        candidate_name: str,
        persona_name: str,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        safe_id = self._validate_id(session_id)
        now = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(session_data, ensure_ascii=False)
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT created_at FROM interview_sessions WHERE session_id = ?",
                (safe_id,)
            ).fetchone()
            created_at = existing["created_at"] if existing else now
            connection.execute(
                """
                INSERT INTO interview_sessions
                    (session_id, candidate_name, persona_name, created_at, updated_at, question_count, session_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    candidate_name = excluded.candidate_name,
                    persona_name = excluded.persona_name,
                    updated_at = excluded.updated_at,
                    question_count = excluded.question_count,
                    session_json = excluded.session_json
                """,
                (
                    safe_id,
                    candidate_name,
                    persona_name,
                    created_at,
                    now,
                    len(session_data.get("session_results", [])),
                    payload
                )
            )
        return {
            "session_id": safe_id,
            "candidate_name": candidate_name,
            "persona_name": persona_name,
            "created_at": created_at,
            "updated_at": now,
            "question_count": len(session_data.get("session_results", []))
        }

    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT session_id, candidate_name, persona_name, created_at, updated_at, question_count
                FROM interview_sessions ORDER BY updated_at DESC LIMIT ?
                """,
                (limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        safe_id = self._validate_id(session_id)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM interview_sessions WHERE session_id = ?",
                (safe_id,)
            ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["session_data"] = json.loads(result.pop("session_json"))
        return result

    def delete(self, session_id: str) -> bool:
        safe_id = self._validate_id(session_id)
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM interview_sessions WHERE session_id = ?",
                (safe_id,)
            )
            return cursor.rowcount > 0
