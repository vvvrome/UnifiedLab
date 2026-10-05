-- UnifiedLab - inicializacion completa de MySQL
-- Ejecutar como root o como una cuenta con permisos para CREATE DATABASE/USER.
-- Este script CREA las bases y TODAS las tablas necesarias.
-- La migracion de los datos SQLite se realiza despues con migrar_sqlite_a_mysql.py.

CREATE DATABASE IF NOT EXISTS unifiedlab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS physiclab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS datacenter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS stellarlab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'unifiedlab'@'localhost' IDENTIFIED BY 'xqgy1ECJ';
GRANT ALL PRIVILEGES ON unifiedlab.* TO 'unifiedlab'@'localhost';
GRANT ALL PRIVILEGES ON physiclab.* TO 'unifiedlab'@'localhost';
GRANT ALL PRIVILEGES ON datacenter.* TO 'unifiedlab'@'localhost';
GRANT ALL PRIVILEGES ON stellarlab.* TO 'unifiedlab'@'localhost';

-- =============================
-- UNIFIEDLAB / PORTAL
-- =============================
USE unifiedlab;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(40) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================
-- PHYSICLAB
-- =============================
USE physiclab;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(40) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(40) NOT NULL,
    section VARCHAR(80) NOT NULL DEFAULT 'general',
    result LONGTEXT NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_history_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================
-- DATACENTER
-- =============================
USE datacenter;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(40) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL,
    active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(40),
    action VARCHAR(100) NOT NULL,
    result VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    details TEXT,
    INDEX idx_audit_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================
-- STELLARLAB
-- =============================
USE stellarlab;

CREATE TABLE IF NOT EXISTS stars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    data LONGTEXT NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stars_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS planets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    data LONGTEXT NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_planets_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

FLUSH PRIVILEGES;

-- Comprobacion rapida:
-- USE unifiedlab; SHOW TABLES;
-- USE physiclab; SHOW TABLES;
-- USE datacenter; SHOW TABLES;
-- USE stellarlab; SHOW TABLES;
