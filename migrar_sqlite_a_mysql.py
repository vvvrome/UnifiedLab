"""Migra los cuatro SQLite incluidos en UnifiedLab a MySQL.

No elimina ni modifica los SQLite de origen. Requiere mysql-connector-python.
"""
from pathlib import Path
import os
import sqlite3
import getpass
import mysql.connector

ROOT = Path(__file__).resolve().parent
BASE = ROOT
MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER", "unifiedlab")
MYSQL_PASSWORD = os.environ.get("xqgy1ECJ")
if MYSQL_PASSWORD is None:
    MYSQL_PASSWORD = getpass.getpass("Contraseña del usuario MySQL: ")

SOURCES = {
    "unifiedlab": BASE / "portal" / "portal_users.db",
    "physiclab": BASE / "PhysicLab" / "physiclab_users.db",
    "datacenter": BASE / "datacenter_original" / "database" / "users.db",
    "stellarlab": BASE / "portal" / "stellar_lab.db",
}


def mysql_server():
    return mysql.connector.connect(host=MYSQL_HOST, port=MYSQL_PORT,
                                   user=MYSQL_USER, password=MYSQL_PASSWORD)




def migrate_unifiedlab(src, conn):
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(40) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    rows = sqlite3.connect(src).execute("SELECT id, username, password_hash, created_at FROM users").fetchall()
    cur.executemany("INSERT IGNORE INTO users (id, username, password_hash, created_at) VALUES (%s,%s,%s,%s)", rows)
    conn.commit(); cur.close()


def migrate_physiclab(src, conn):
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(40) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'user',
        created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    cur.execute("""CREATE TABLE IF NOT EXISTS history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(40) NOT NULL,
        section VARCHAR(80) NOT NULL DEFAULT 'general',
        result LONGTEXT NOT NULL,
        created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_history_username (username)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    db=sqlite3.connect(src); db.row_factory=sqlite3.Row
    users=[tuple(r) for r in db.execute("SELECT id,username,password_hash,role,created_at FROM users")]
    hist=[tuple(r) for r in db.execute("SELECT id,username,section,result,created_at FROM history")]
    cur.executemany("INSERT IGNORE INTO users (id,username,password_hash,role,created_at) VALUES (%s,%s,%s,%s,%s)", users)
    cur.executemany("INSERT IGNORE INTO history (id,username,section,result,created_at) VALUES (%s,%s,%s,%s,%s)", hist)
    conn.commit(); db.close(); cur.close()


def migrate_datacenter(src, conn):
    cur=conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(40) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(10) NOT NULL,
        active TINYINT(1) NOT NULL DEFAULT 1,
        created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    cur.execute("""CREATE TABLE IF NOT EXISTS audit_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
        username VARCHAR(40), action VARCHAR(100) NOT NULL,
        result VARCHAR(100) NOT NULL, ip_address VARCHAR(45),
        user_agent TEXT, details TEXT,
        INDEX idx_audit_timestamp (timestamp)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    db=sqlite3.connect(src); db.row_factory=sqlite3.Row
    users=[tuple(r) for r in db.execute("SELECT id,username,password_hash,role,active,created_at,last_login FROM users")]
    logs=[tuple(r) for r in db.execute("SELECT id,timestamp,username,action,result,ip_address,user_agent,details FROM audit_log")]
    cur.executemany("INSERT IGNORE INTO users (id,username,password_hash,role,active,created_at,last_login) VALUES (%s,%s,%s,%s,%s,%s,%s)", users)
    cur.executemany("INSERT IGNORE INTO audit_log (id,timestamp,username,action,result,ip_address,user_agent,details) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", logs)
    conn.commit(); db.close(); cur.close()


def migrate_stellar(src, conn):
    cur=conn.cursor()
    for table in ('stars','planets'):
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {table} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            data LONGTEXT NOT NULL,
            created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_{table}_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    db=sqlite3.connect(src); db.row_factory=sqlite3.Row
    for table in ('stars','planets'):
        rows=[tuple(r) for r in db.execute(f"SELECT id,user_id,data,created_at FROM {table}")]
        cur.executemany(f"INSERT IGNORE INTO {table} (id,user_id,data,created_at) VALUES (%s,%s,%s,%s)", rows)
    conn.commit(); db.close(); cur.close()


MIGRATORS={'unifiedlab':migrate_unifiedlab,'physiclab':migrate_physiclab,'datacenter':migrate_datacenter,'stellarlab':migrate_stellar}


def main():
    # Las bases ya deben existir tras ejecutar mysql_setup.sql.
    # El usuario configurado solo necesita permisos sobre esas bases.
    for db_name, src in SOURCES.items():
        if not src.exists():
            print(f"[WARN] No existe {src}; se omite {db_name}")
            continue

        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=db_name,
            )
        except mysql.connector.Error as exc:
            print(f"[ERROR] No se puede conectar a {db_name}: {exc}")
            continue

        print(f"[INFO] Migrando {db_name} desde {src.name}...")
        try:
            MIGRATORS[db_name](src, conn)
            print(f"[OK] {db_name} migrada.")
        except Exception as exc:
            conn.rollback()
            print(f"[ERROR] Fallo migrando {db_name}: {exc}")
        finally:
            conn.close()

    print("[OK] Migración terminada. Los SQLite originales no se han modificado.")


if __name__ == '__main__':
    main()
