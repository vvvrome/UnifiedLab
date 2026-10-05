import os
import mysql.connector
from mysql.connector import IntegrityError

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "xqgy1ECJ"),
    "database": os.environ.get(
        "MYSQL_DATABASE_DATACENTER",
        "datacenter"
    ),
}


def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)


def init_database():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (

                id INT AUTO_INCREMENT PRIMARY KEY,

                username VARCHAR(40) NOT NULL UNIQUE,

                password_hash VARCHAR(255) NOT NULL,

                role VARCHAR(10) NOT NULL,

                active TINYINT(1) NOT NULL DEFAULT 1,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                last_login TIMESTAMP NULL

            ) ENGINE=InnoDB
              DEFAULT CHARSET=utf8mb4
              COLLATE=utf8mb4_unicode_ci
        """)

        connection.commit()

    finally:
        connection.close()


def create_user(username, password, role="VIEWER"):

    connection = get_connection()

    password_hash = generate_password_hash(password)

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password_hash,
                role
            )
            VALUES (%s, %s, %s)
            """,
            (
                username,
                password_hash,
                role
            )
        )

        connection.commit()

        return True

    except IntegrityError:

        connection.rollback()

        return False

    finally:

        connection.close()


def authenticate_user(username, password):

    connection = get_connection()

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE username = %s
            AND active = 1
            """,
            (username,)
        )

        user = cursor.fetchone()

    finally:

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

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
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
        )

        users = cursor.fetchall()

    finally:

        connection.close()

    return [dict(user) for user in users]


def get_user_by_username(username):

    connection = get_connection()

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE username = %s
            AND active = 1
            """,
            (username,)
        )

        user = cursor.fetchone()

    finally:

        connection.close()

    if user is None:
        return None

    return dict(user)