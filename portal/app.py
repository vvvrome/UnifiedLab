from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from functools import wraps
from urllib.parse import urlparse

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from Quimica.routes import stellar_bp

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "portal_users.db"

app = Flask(__name__)
app.secret_key = os.environ.get("UNIFIEDLAB_SECRET_KEY") or os.urandom(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("UNIFIEDLAB_COOKIE_SECURE", "0") == "1",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 8,
)


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL COLLATE NOCASE UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


init_db()
app.register_blueprint(stellar_bp)

@app.get("/")
@login_required
def index():
    return render_template("dashboard.html", username=session.get("username"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("password_confirm", "")
        if not 3 <= len(username) <= 40:
            flash("El usuario debe tener entre 3 y 40 caracteres.", "error")
        elif len(password) < 10:
            flash("La contraseña debe tener al menos 10 caracteres.", "error")
        elif password != confirm:
            flash("Las contraseñas no coinciden.", "error")
        else:
            try:
                with connect_db() as conn:
                    conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                                 (username, generate_password_hash(password)))
                flash("Cuenta creada. Ya puedes iniciar sesión.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Ese nombre de usuario ya existe.", "error")
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with connect_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session.permanent = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            target = request.form.get("next", "")
            # Prevent open redirects: only allow local paths.
            if target.startswith("/") and not target.startswith("//"):
                return redirect(target)
            return redirect(url_for("index"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("auth.html", mode="login")

@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/health")
def health():
    return {"status": "ok", "service": "UnifiedLab Portal"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
