import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from .config import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    active_path = os.getenv("DB_PATH", DB_PATH)
    conn = sqlite3.connect(active_path, timeout=15.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _ensure_tables(conn)
    return conn

def _ensure_tables(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
        content TEXT NOT NULL,
        audio_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS case_state (
        session_id TEXT PRIMARY KEY,
        domain TEXT DEFAULT 'unknown',
        facts_json TEXT NOT NULL,
        is_complete BOOLEAN DEFAULT FALSE,
        escalation_triggered BOOLEAN DEFAULT FALSE,
        escalation_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()

def init_db():
    """Initializes SQLite database tables if they do not exist."""
    with get_db_connection() as conn:
        _ensure_tables(conn)

def save_chat_message(session_id: str, role: str, content: str, audio_url: Optional[str] = None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_history (session_id, role, content, audio_url)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, content, audio_url))
        conn.commit()

def get_chat_history(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content, audio_url, created_at 
            FROM chat_history 
            WHERE session_id = ? 
            ORDER BY id ASC
        """, (session_id,))
        rows = cursor.fetchall()
        # Return the most recent `limit` messages
        messages = [dict(row) for row in rows]
        return messages[-limit:] if limit else messages

def get_case_state(session_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, domain, facts_json, is_complete, escalation_triggered, escalation_reason, updated_at
            FROM case_state
            WHERE session_id = ?
        """, (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        data = dict(row)
        try:
            data["facts"] = json.loads(data["facts_json"])
        except Exception:
            data["facts"] = {}
        data["is_complete"] = bool(data["is_complete"])
        data["escalation_triggered"] = bool(data["escalation_triggered"])
        return data

def upsert_case_state(
    session_id: str,
    domain: str,
    facts: Dict[str, Any],
    is_complete: bool = False,
    escalation_triggered: bool = False,
    escalation_reason: Optional[str] = None
):
    facts_json = json.dumps(facts, ensure_ascii=False)
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO case_state (session_id, domain, facts_json, is_complete, escalation_triggered, escalation_reason, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                domain = excluded.domain,
                facts_json = excluded.facts_json,
                is_complete = excluded.is_complete,
                escalation_triggered = excluded.escalation_triggered,
                escalation_reason = excluded.escalation_reason,
                updated_at = excluded.updated_at
        """, (session_id, domain, facts_json, is_complete, escalation_triggered, escalation_reason, now))
        conn.commit()

# Automatically ensure tables exist on module import (crucial for serverless/Streamlit Cloud in-process mode)
try:
    init_db()
except Exception:
    pass

if __name__ == "__main__":
    init_db()
    print("ai_lawyer.db successfully initialized with tables chat_history and case_state.")
