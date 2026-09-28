import sqlite3
from pathlib import Path

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "users.db"


def get_connection():

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            role TEXT NOT NULL
                CHECK(role IN ('ADMIN', 'VIEWER')),

            active INTEGER NOT NULL DEFAULT 1,

            created_at
                TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            last_login
                TIMESTAMP NULL
        )
    """)

    connection.commit()

    connection.close()


def create_user(username, password, role="VIEWER"):

    connection = get_connection()

    password_hash = generate_password_hash(password)

    try:

        connection.execute(
            """
            INSERT INTO users
            (
                username,
                password_hash,
                role
            )
            VALUES (?, ?, ?)
            """,
            (
                username,
                password_hash,
                role
            )
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def authenticate_user(username, password):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        AND active = 1
        """,
        (username,)
    ).fetchone()

    connection.close()

    if user is None:
        return None

    if not check_password_hash(
        user["password_hash"],
        password
    ):
        return None

    return dict(user)


def get_all_users():

    connection = get_connection()

    users = connection.execute(
        """
        SELECT
            id,
            username,
            role,
            active,
            created_at,
            last_login
        FROM users
        ORDER BY id ASC
        """
    ).fetchall()

    connection.close()

    return [dict(user) for user in users]

def get_user_by_username(username):
    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        AND active = 1
        """,
        (username,)
    ).fetchone()

    connection.close()

    if user is None:
        return None

    return dict(user)