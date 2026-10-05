import os
import mysql.connector


MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "unifiedlab"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get(
        "MYSQL_DATABASE_DATACENTER",
        "datacenter"
    ),
}


def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)


def init_audit_database():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (

                id INT AUTO_INCREMENT PRIMARY KEY,

                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                username VARCHAR(100),

                action VARCHAR(100) NOT NULL,

                result VARCHAR(100) NOT NULL,

                ip_address VARCHAR(45),

                user_agent TEXT,

                details TEXT

            ) ENGINE=InnoDB
              DEFAULT CHARSET=utf8mb4
              COLLATE=utf8mb4_unicode_ci
        """)

        connection.commit()

    finally:

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

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO audit_log (
                username,
                action,
                result,
                ip_address,
                user_agent,
                details
            )
            VALUES (%s, %s, %s, %s, %s, %s)
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

    finally:

        connection.close()


def get_audit_logs(limit=200):

    connection = get_connection()

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
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
            LIMIT %s
            """,
            (limit,)
        )

        logs = cursor.fetchall()

    finally:

        connection.close()

    return [dict(log) for log in logs]