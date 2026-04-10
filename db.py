import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "users.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                preferences TEXT DEFAULT '',
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0
            )
        """)
        conn.commit()


def get_preferences(user_id: str) -> str:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT preferences FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row["preferences"] if row else ""


def set_preferences(user_id: str, preferences: str) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO users (user_id, preferences)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET preferences = excluded.preferences
        """, (user_id, preferences))
        conn.commit()


def add_tokens(user_id: str, input_tokens: int, output_tokens: int) -> None:
    with get_connection() as conn:
        conn.execute("""
            UPDATE users SET
                input_tokens = input_tokens + ?,
                output_tokens = output_tokens + ?
            WHERE user_id = ?
        """, (input_tokens, output_tokens, user_id))
        conn.commit()


def ensure_user(user_id: str, name: str) -> None:
    """Create user row if it doesn't exist yet."""
    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO users (user_id, name, preferences)
            VALUES (?, ?, '')
        """, (user_id, name))
        conn.commit()
