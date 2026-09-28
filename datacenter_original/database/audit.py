import sqlite3
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "users.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_audit_database():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            username TEXT,

            action TEXT NOT NULL,

            result TEXT NOT NULL,

            ip_address TEXT,

            user_agent TEXT,

            details TEXT
        )
    """)

    connection.commit()
    connection.close()


def log_event(
    username,
    action,
    result,
    ip_address=None,
    user_agent=None,
    details=None
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO audit_log (
            username,
            action,
            result,
            ip_address,
            user_agent,
            details
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            action,
            result,
            ip_address,
            user_agent,
            details
        )
    )

    connection.commit()
    connection.close()


def get_audit_logs(limit=200):

    connection = get_connection()

    logs = connection.execute(
        """
        SELECT
            id,
            timestamp,
            username,
            action,
            result,
            ip_address,
            user_agent,
            details
        FROM audit_log
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    connection.close()

    return [dict(log) for log in logs]