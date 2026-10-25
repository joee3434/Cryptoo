import sqlite3
from datetime import datetime

DB_NAME = "cryptoo_history.db"


def _connect():
    con = sqlite3.connect(DB_NAME)
    con.execute("PRAGMA journal_mode=WAL")
    return con


def init_db():
    with _connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                algorithm TEXT NOT NULL,
                operation TEXT NOT NULL,
                input_text TEXT NOT NULL,
                output_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                elapsed_ms REAL NOT NULL
            )
        """)


def add_record(algorithm, operation, input_text, output_text, elapsed_ms):
    with _connect() as con:
        con.execute(
            """INSERT INTO operations
            (algorithm, operation, input_text, output_text, created_at, elapsed_ms)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (algorithm, operation, input_text, output_text,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), elapsed_ms),
        )


def get_history(limit=20):
    with _connect() as con:
        return con.execute(
            """SELECT id, algorithm, operation, input_text, output_text, created_at, elapsed_ms
            FROM operations ORDER BY id DESC LIMIT ?""", (limit,)
        ).fetchall()


def clear_history():
    with _connect() as con:
        con.execute("DELETE FROM operations")
