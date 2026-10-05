from __future__ import annotations

import json
import os
import mysql.connector

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from mysql.connector import IntegrityError

from .orbital_simulator import OrbitalSimulator
from .planet_model import Planet
from .star_model import Star
from .stellar_physics import analizar_estrella

stellar_bp = Blueprint(
    "stellar",
    __name__,
    url_prefix="/stellar",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)

MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "unifiedlab"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE_STELLAR", "stellarlab"),
}


class DB:
    def __init__(self):
        self.conn = mysql.connector.connect(**MYSQL_CONFIG)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()

    def execute(self, sql, params=()):
        cur = self.conn.cursor(dictionary=True)
        cur.execute(sql.replace("?", "%s"), params)
        return cur


def connect_db():
    return DB()


def init_db():
    with connect_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS stars (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                data LONGTEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(40) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS planets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                data LONGTEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""
        )


def current_user_id():
    return session.get("stellar_user_id")


def login_guard():
    # UnifiedLab debe estar autenticado primero. StellarLab añade su propia
    # credencial después, aunque ambos viven en el mismo proceso Flask.
    if not session.get("user_id"):
        return redirect(url_for("login", next=request.path))

    stellar_user_id = session.get("stellar_user_id")
    if not stellar_user_id:
        return redirect(url_for("stellar.login", next=request.path))

    with connect_db() as conn:
        user = conn.execute(
            "SELECT id, username, role FROM users WHERE id = ?",
            (stellar_user_id,),
        ).fetchone()
    if not user or user["username"].casefold() != session.get("username", "").casefold():
        session.pop("stellar_user_id", None)
        session.pop("stellar_username", None)
        return redirect(url_for("stellar.login", next=request.path))
    return None


init_db()


@stellar_bp.before_request
def require_login():
    if request.endpoint in {"stellar.login", "stellar.register", "stellar.static"}:
        return None
    return login_guard()


@stellar_bp.route("/login", methods=["GET", "POST"])
def login():
    # Esta pantalla solo aparece después del login principal de UnifiedLab.
    if not session.get("user_id"):
        return redirect(url_for("login", next=request.path))

    portal_username = session.get("username", "")
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username.casefold() != portal_username.casefold():
            error = "Debes utilizar el mismo usuario que has autenticado en UnifiedLab."
        else:
            with connect_db() as conn:
                user = conn.execute(
                    "SELECT * FROM users WHERE username = ?", (username,)
                ).fetchone()
            if user and check_password_hash(user["password_hash"], password):
                session["stellar_user_id"] = user["id"]
                session["stellar_username"] = user["username"]
                destination = request.args.get("next", "")
                if not (destination.startswith("/stellar") and not destination.startswith("//")):
                    destination = url_for("stellar.index")
                return redirect(destination)
            error = "Usuario o contraseña de StellarLab incorrectos."

    return render_template("stellar_login.html", error=error, username=portal_username)


@stellar_bp.route("/register", methods=["GET", "POST"])
def register():
    if not session.get("user_id"):
        return redirect(url_for("login", next=request.path))

    username = session.get("username", "")
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("password_confirm", "")
        if len(password) < 10:
            error = "La contraseña debe tener al menos 10 caracteres."
        elif password != confirm:
            error = "Las contraseñas no coinciden."
        else:
            try:
                with connect_db() as conn:
                    conn.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username, generate_password_hash(password)),
                    )
                return redirect(url_for("stellar.login"))
            except IntegrityError:
                error = "Ya existe una credencial de StellarLab para este usuario."

    return render_template("stellar_register.html", error=error, username=username)


@stellar_bp.post("/logout")
def logout():
    session.pop("stellar_user_id", None)
    session.pop("stellar_username", None)
    return redirect(url_for("stellar.login"))


@stellar_bp.get("/")
def index():
    user_id = current_user_id()
    with connect_db() as conn:
        stars = conn.execute(
            "SELECT id, data, created_at FROM stars WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        ).fetchall()
        planets = conn.execute(
            "SELECT id, data, created_at FROM planets WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        ).fetchall()

    stars = [(row["id"], json.loads(row["data"]), row["created_at"]) for row in stars]
    planets = [(row["id"], json.loads(row["data"]), row["created_at"]) for row in planets]
    return render_template("stellar_index.html", stars=stars, planets=planets)


@stellar_bp.route("/estrella", methods=["GET", "POST"])
def estrella():
    if request.method == "POST":
        try:
            star = Star.desde_formulario(request.form)
            data = star.to_dict()
            analysis = analizar_estrella(star)
            data["analisis"] = analysis
            with connect_db() as conn:
                conn.execute(
                    "INSERT INTO stars (user_id, data) VALUES (?, ?)",
                    (current_user_id(), json.dumps(data, ensure_ascii=False)),
                )
            flash(f"Estrella '{star.nombre}' creada correctamente.", "success")
            return redirect(url_for("stellar.index"))
        except (ValueError, TypeError, KeyError) as exc:
            flash(str(exc), "error")

    return render_template("formulario_estrella.html")


@stellar_bp.route("/planeta", methods=["GET", "POST"])
def planeta():
    if request.method == "POST":
        try:
            planet = Planet.desde_formulario(request.form)
            data = planet.to_dict()
            with connect_db() as conn:
                conn.execute(
                    "INSERT INTO planets (user_id, data) VALUES (?, ?)",
                    (current_user_id(), json.dumps(data, ensure_ascii=False)),
                )
            flash(f"Planeta '{planet.nombre}' creado correctamente.", "success")
            return redirect(url_for("stellar.index"))
        except (ValueError, TypeError, KeyError) as exc:
            flash(str(exc), "error")

    return render_template("formulario_planeta.html")


@stellar_bp.route("/orbita", methods=["GET", "POST"])
def orbita():
    user_id = current_user_id()
    with connect_db() as conn:
        star_rows = conn.execute(
            "SELECT id, data FROM stars WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        ).fetchall()
        planet_rows = conn.execute(
            "SELECT id, data FROM planets WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        ).fetchall()

    if not star_rows:
        flash("Primero necesitas crear al menos una estrella.", "error")
        return redirect(url_for("stellar.estrella"))

    selected_star_id = request.values.get("star_id", str(star_rows[0]["id"]))
    try:
        selected_star_id = int(selected_star_id)
    except ValueError:
        selected_star_id = star_rows[0]["id"]

    selected_star_row = next(
        (row for row in star_rows if row["id"] == selected_star_id), star_rows[0]
    )
    selected_star_data = json.loads(selected_star_row["data"])
    selected_star = Star(**{k: selected_star_data[k] for k in (
        "nombre", "tipo", "masa", "radio", "temperatura", "luminosidad", "edad", "metallicidad", "composicion", "abundancia"
    )})

    selected_planet_ids = request.values.getlist("planet_id")
    if selected_planet_ids:
        allowed = {str(row["id"]): row for row in planet_rows}
        chosen_rows = [allowed[value] for value in selected_planet_ids if value in allowed]
    else:
        chosen_rows = planet_rows

    planets = []
    for row in chosen_rows:
        data = json.loads(row["data"])
        planets.append(Planet(**data))

    result = None
    if request.method == "POST":
        try:
            days = float(request.form.get("dias", 365))
            dt_hours = float(request.form.get("paso_horas", 6))
            if days <= 0 or dt_hours <= 0:
                raise ValueError("Los días y el paso temporal deben ser positivos.")
            simulator = OrbitalSimulator(selected_star, planets)
            result = simulator.simular(days * 86400, dt_hours * 3600)
            result["posiciones_mostradas"] = [
                [
                    [[round(float(x) / 1.495978707e11, 6), round(float(y) / 1.495978707e11, 6)] for x, y in frame]
                    for frame in result["posiciones"][::max(1, len(result["posiciones"]) // 500)]
                ]
            ][0]
            result["planetas"] = [planet.to_dict() for planet in planets]
            result["estrella"] = selected_star.to_dict()
            result["pasos"] = len(result["posiciones"])
            result["dias"] = days
        except (ValueError, TypeError, FloatingPointError) as exc:
            flash(str(exc), "error")

    stars = [(row["id"], json.loads(row["data"])) for row in star_rows]
    planets_data = [(row["id"], json.loads(row["data"])) for row in planet_rows]
    return render_template(
        "simular_orbital.html",
        stars=stars,
        planets=planets_data,
        selected_star_id=selected_star_row["id"],
        selected_planet_ids=[row["id"] for row in chosen_rows],
        result=result,
    )


@stellar_bp.get("/estrella/<int:star_id>")
def detalle_estrella(star_id):
    with connect_db() as conn:
        row = conn.execute(
            "SELECT data FROM stars WHERE id = ? AND user_id = ?",
            (star_id, current_user_id()),
        ).fetchone()
    if not row:
        flash("No se ha encontrado esa estrella.", "error")
        return redirect(url_for("stellar.index"))
    return render_template("detalle_estrella.html", star=json.loads(row["data"]))
