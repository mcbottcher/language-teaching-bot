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
                telegram_id INTEGER PRIMARY KEY,
                name TEXT,
                preferences TEXT DEFAULT '',
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0
            )
        """)
        for col in ("input_tokens", "output_tokens"):
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {col} INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass
        conn.commit()


def get_preferences(telegram_id: int) -> str:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT preferences FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return row["preferences"] if row else ""


def set_preferences(telegram_id: int, preferences: str) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO users (telegram_id, preferences)
            VALUES (?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET preferences = excluded.preferences
        """, (telegram_id, preferences))
        conn.commit()


def add_tokens(telegram_id: int, input_tokens: int, output_tokens: int) -> None:
    with get_connection() as conn:
        conn.execute("""
            UPDATE users SET
                input_tokens = input_tokens + ?,
                output_tokens = output_tokens + ?
            WHERE telegram_id = ?
        """, (input_tokens, output_tokens, telegram_id))
        conn.commit()


def ensure_user(telegram_id: int, name: str) -> None:
    """Create user row if it doesn't exist yet."""
    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO users (telegram_id, name, preferences)
            VALUES (?, ?, '')
        """, (telegram_id, name))
        conn.commit()
