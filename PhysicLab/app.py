from __future__ import annotations

from typing import Any, Dict
import numpy as np
from flask import Flask, jsonify, render_template, request, send_file, redirect, url_for, session, g
from sympy import E as EULER, cos, diff, exp, integrate, log, pi, sin, simplify, sqrt, symbols, tan
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from python.Algebra import (
    analizar_sistema,
    autovalores_autovectores,
    calcular_determinante,
    convertir_formulario,
    derivada_numerica,
    integrar_numerica,
    inversa_matriz,
    matriz_rotacion_2d,
    producto_escalar,
    producto_vectorial,
    transformar_vector,
)
from python.Fisica_I import (
    simulacion_proyectil,
    caida_libre,
    fuerza_lorentz,
    movimiento_mru,
    movimiento_mrua,
    cinematica_nd,
    transformar_frame,
    fuerza_rozamiento,
    energia_cinetica,
    energia_potencial_gravitatoria,
    colision_unidimensional,
    oscilador_armonico,
    sistema_acoplado_dos_masas,
    doble_pendulo,
)
import io
import base64
import os
import uuid
import mysql.connector
from mysql.connector import IntegrityError
import json
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)
# En producción define PHYSICLAB_SECRET_KEY como variable de entorno.
app.secret_key = os.environ.get("PHYSICLAB_SECRET_KEY") or os.urandom(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("PHYSICLAB_COOKIE_SECURE", "0") == "1",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 8,
)
MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "unifiedlab"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE_PHYSICLAB", "physiclab"),
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


def get_auth_db():
    return DB()
RESERVED_USERNAMES = {"admin", "administrator", "root"}


def log_operation(section: str, operation: str, inputs: dict, result: str):
    """Registra una operación completada para el usuario autenticado."""
    try:
        details = json.dumps(inputs, ensure_ascii=False, default=str)
        text = f"Operación: {operation}\nEntradas: {details}\nResultado: {result}"
        with get_auth_db() as conn:
            conn.execute(
                "INSERT INTO history (username, section, result) VALUES (?, ?, ?)",
                (g.current_user, section, text),
            )
    except Exception:
        # El fallo del registro no debe tumbar un cálculo válido; queda en el log del servidor.
        app.logger.exception("No se pudo registrar la operación en el historial")


def init_auth_db():
    with get_auth_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(40) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
        conn.execute("""CREATE TABLE IF NOT EXISTS history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(40) NOT NULL,
            section VARCHAR(80) NOT NULL DEFAULT 'general',
            result LONGTEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
        # Los roles administrativos anteriores no se consideran fiables.
        # Solo la cuenta provisionada desde el entorno puede recibir el rol admin.
        conn.execute("UPDATE users SET role = 'user' WHERE role = 'admin'")
        admin_username = os.environ.get("PHYSICLAB_ADMIN_USERNAME", "").strip()
        admin_password = os.environ.get("PHYSICLAB_ADMIN_PASSWORD", "")
        if admin_username and admin_password:
            password_hash = generate_password_hash(admin_password)
            existing = conn.execute(
                "SELECT id FROM users WHERE username = ?", (admin_username,)
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE users SET password_hash = ?, role = 'admin' WHERE id = ?",
                    (password_hash, existing["id"]),
                )
            else:
                conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
                    (admin_username, password_hash),
                )


init_auth_db()


@app.before_request
def require_login():
    public_endpoints = {"login", "register", "static"}
    if request.endpoint in public_endpoints:
        return None

    user_id = session.get("user_id")
    if not user_id:
        if request.path.startswith("/api/"):
            return jsonify({"error": "Autenticación requerida."}), 401
        return redirect(url_for("login", next=request.path))

    # No confiar en el rol guardado en la cookie: leerlo de SQLite en cada petición.
    with get_auth_db() as conn:
        user = conn.execute(
            "SELECT id, username, role FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    if not user:
        session.clear()
        if request.path.startswith("/api/"):
            return jsonify({"error": "Sesión no válida."}), 401
        return redirect(url_for("login"))

    g.current_user = user["username"]
    g.current_role = user["role"] if user["role"] == "admin" else "user"
    session["username"] = user["username"]
    session["role"] = g.current_role

    # El panel de historial global no se sirve a cuentas normales, ni por URL directa.
    if request.path == "/historial" and g.current_role != "admin":
        return "Acceso denegado: se requiere el rol de administrador.", 403


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_auth_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session.permanent = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            # El rol se vuelve a consultar desde la base de datos en cada petición.
            session["role"] = "admin" if user["role"] == "admin" else "user"
            return redirect("/")
        error = "Usuario o contraseña incorrectos."
    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("password_confirm", "")
        if len(username) < 3 or len(username) > 40:
            error = "El usuario debe tener entre 3 y 40 caracteres."
        elif username.casefold() in RESERVED_USERNAMES:
            error = "Ese nombre está reservado y no se puede registrar."
        elif len(password) < 8:
            error = "La contraseña debe tener al menos 8 caracteres."
        elif password != confirm:
            error = "Las contraseñas no coinciden."
        else:
            try:
                with get_auth_db() as conn:
                    conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                                 (username, generate_password_hash(password)))
                return redirect(url_for("login", registered="1"))
            except IntegrityError:
                error = "Ese nombre de usuario ya está registrado."
    return render_template("register.html", error=error)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))



def parse_matrix_2x2(form: Dict[str, Any]) -> np.ndarray:
    return np.array(
        [
            [float(form.get("a", 0)), float(form.get("b", 0))],
            [float(form.get("c", 0)), float(form.get("d", 0))],
        ],
        dtype=float,
    )


def parse_vector_3d(form: Dict[str, Any]) -> np.ndarray:
    return np.array(
        [
            float(form.get("vx", 0)),
            float(form.get("vy", 0)),
            float(form.get("vz", 0)),
        ],
        dtype=float,
    )


def parse_float_field(form: Dict[str, Any], name: str, default: Any = None, required: bool = False, min_val: float | None = None, max_val: float | None = None):
    """Intento seguro de leer un campo numérico del formulario.
    Devuelve (valor, error_message).
    """
    s = form.get(name)
    if s is None or s == "":
        if required and default is None:
            return None, f"Campo '{name}' requerido."
        try:
            return (float(default) if default is not None else None), None
        except Exception:
            return None, f"Valor por defecto invalido para '{name}'."
    try:
        val = float(s)
    except Exception:
        return None, f"El campo '{name}' debe ser un numero valido."
    if min_val is not None and val < min_val:
        return val, f"El campo '{name}' debe ser >= {min_val}."
    if max_val is not None and val > max_val:
        return val, f"El campo '{name}' debe ser <= {max_val}."
    return val, None


def evaluar_expresion(expr: str) -> float:
    if not expr or not expr.strip():
        raise ValueError("Escribe una funcion valida, por ejemplo x**2 + sin(x)")

    x = symbols("x")
    allowed = {
        "x": x,
        "sin": sin,
        "cos": cos,
        "tan": tan,
        "exp": exp,
        "log": log,
        "sqrt": sqrt,
        "pi": pi,
        "e": EULER,
        "abs": abs,
    }

    try:
        parsed = parse_expr(
            expr,
            local_dict=allowed,
            transformations=(standard_transformations + (implicit_multiplication_application,)),
            evaluate=True,
        )
    except Exception as exc:
        raise ValueError(f"Expresion no valida: {exc}") from exc

    free_symbols = getattr(parsed, "free_symbols", set())
    if free_symbols - {x}:
        raise ValueError("Solo se permite la variable x y funciones matematicas seguras.")

    try:
        return float(parsed.subs(x, 0).evalf())
    except Exception as exc:
        raise ValueError(f"No se pudo evaluar la expresion: {exc}") from exc


def parsear_expresion(expr: str):
    """Parsea expresiones educativas usando únicamente símbolos y funciones permitidos."""
    if not expr or not expr.strip():
        raise ValueError("Escribe una funcion valida, por ejemplo x**2 + sin(x)")
    x = symbols("x")
    try:
        parsed = parse_expr(
            expr,
            local_dict={"x": x, "sin": sin, "cos": cos, "tan": tan, "exp": exp,
                        "log": log, "sqrt": sqrt, "pi": pi, "e": EULER, "abs": abs},
            transformations=(standard_transformations + (implicit_multiplication_application,)),
            evaluate=True,
        )
    except Exception as exc:
        raise ValueError(f"Expresion no valida: {exc}") from exc
    if parsed.free_symbols - {x}:
        raise ValueError("Solo se permite la variable x y funciones matematicas seguras.")
    return x, parsed


def calculo_interactivo(expr: str, a: float, b: float, muestras: int = 160) -> dict[str, Any]:
    if a >= b:
        raise ValueError("El intervalo debe cumplir a < b.")
    if not 20 <= muestras <= 800:
        raise ValueError("El numero de muestras debe estar entre 20 y 800.")
    x, parsed = parsear_expresion(expr)
    derivada = simplify(diff(parsed, x))
    integral = simplify(integrate(parsed, x))
    integral_definida = integrate(parsed, (x, a, b))
    valores_x = np.linspace(a, b, muestras)
    valores_y = [float(parsed.subs(x, value).evalf()) for value in valores_x]
    valores_d = [float(derivada.subs(x, value).evalf()) for value in valores_x]
    pasos = [
        f"1. Funcion: f(x) = {parsed}",
        f"2. Derivada: f'(x) = d/dx({parsed}) = {derivada}",
        f"3. Primitiva: integral de f(x) dx = {integral}",
        f"4. Integral definida: [{integral}]_{a}^{b} = {simplify(integral_definida)}",
    ]
    return {
        "expr": str(parsed), "derivada": str(derivada), "integral": str(integral),
        "integral_definida": float(integral_definida.evalf()), "pasos": pasos,
        "x": valores_x.tolist(), "y": valores_y, "derivada_y": valores_d,
    }


def ejercicio_cinematica():
    x0 = np.random.uniform(-10, 10)
    v = np.random.uniform(-5, 5)
    t = np.random.uniform(1, 10)

    respuesta = x0 + v * t

    return {
        "tema": "cinematica", "dificultad": "facil",
        "question": f"Un objeto parte de la posición x0={x0:.2f} m y se mueve con velocidad constante v={v:.2f} m/s durante t={t:.2f} s. ¿Cuál es su posición final?",
        "answer": respuesta, "unit": "m"
    }

def ejercicio_calculo():
    a = np.random.uniform(0, 5)
    b = np.random.uniform(a + 1, a + 10)
    expr = "x**2 + 2*x + 1"
    x, parsed = parsear_expresion(expr)
    integral_definida = integrate(parsed, (x, a, b))

    return {
        "tema": "calculo", "dificultad": "intermedio",
        "question": f"Calcula la integral definida de f(x) = {parsed} desde x={a:.2f} hasta x={b:.2f}.",
        "answer": float(integral_definida.evalf()), "unit": ""
    }

def ejercicio_energia():
    m = np.random.uniform(1, 10)
    v = np.random.uniform(0, 20)
    respuesta = 0.5 * m * v ** 2

    return {
        "tema": "energia", "dificultad": "facil",
        "question": f"Calcula la energía cinética de un objeto con masa m={m:.2f} kg y velocidad v={v:.2f} m/s.",
        "answer": respuesta, "unit": "J"
    }

EJERCICIOS = [ejercicio_cinematica(), ejercicio_calculo(), ejercicio_energia()]

@app.route("/api/calculo", methods=["POST"])
def api_calculo():
    try:
        data = request.get_json(silent=True) or request.form
        resultado = calculo_interactivo(
            str(data.get("expr", "x**2")), float(data.get("a", 0)),
            float(data.get("b", 3)), int(data.get("muestras", 160)),
        )
        log_operation("calculo", "Cálculo de función/derivada/integral", dict(data), json.dumps(resultado, ensure_ascii=False, default=str))
        return jsonify(resultado)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/ejercicios", methods=["GET"])
def api_ejercicios():
    tema = request.args.get("tema")
    dificultad = request.args.get("dificultad")
    ejercicios = [item for item in EJERCICIOS if
                  (not tema or item["tema"] == tema) and
                  (not dificultad or item["dificultad"] == dificultad)]
    return jsonify([{key: value for key, value in item.items() if key != "answer"} for item in ejercicios])


@app.route("/api/ejercicios/<int:exercise_id>", methods=["POST"])
def api_corregir_ejercicio(exercise_id: int):
    exercise = next((item for item in EJERCICIOS if item["id"] == exercise_id), None)
    if exercise is None:
        return jsonify({"error": "Ejercicio no encontrado"}), 404
    try:
        data = request.get_json(silent=True) or request.form
        answer = float(data.get("answer"))
        correct = abs(answer - exercise["answer"]) <= 1e-6
        response = {"correct": correct, "expected": exercise["answer"], "unit": exercise["unit"]}
        log_operation("ejercicios", f"Corrección ejercicio {exercise_id}", {"respuesta": answer, "pregunta": exercise["question"]}, json.dumps(response, ensure_ascii=False))
        return jsonify(response)
    except (TypeError, ValueError):
        return jsonify({"error": "La respuesta debe ser numerica"}), 400


@app.route("/api/simulador", methods=["POST"])
def api_simulador():
    try:
        data = request.get_json(silent=True) or request.form
        x0 = float(data.get("x0", 0)); v0 = float(data.get("v0", 2))
        a = float(data.get("a", -0.5)); m = float(data.get("m", 1))
        tiempo = float(data.get("t", 10)); muestras = min(max(int(data.get("muestras", 120)), 20), 500)
        if tiempo < 0 or m <= 0:
            raise ValueError("El tiempo debe ser no negativo y la masa positiva.")
        t = np.linspace(0, tiempo, muestras)
        x = x0 + v0 * t + 0.5 * a * t ** 2
        v = v0 + a * t
        energia = 0.5 * m * v ** 2
        response = {"t": t.tolist(), "x": x.tolist(), "v": v.tolist(), "energia": energia.tolist(),
                    "final": {"x": float(x[-1]), "v": float(v[-1]), "energia": float(energia[-1])}}
        log_operation("simulador", "Simulación de movimiento", {"x0": x0, "v0": v0, "a": a, "masa": m, "tiempo": tiempo, "muestras": muestras}, json.dumps(response["final"], ensure_ascii=False))
        return jsonify(response)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/laboratorio3d", methods=["GET"])
def api_laboratorio_3d():
    theta = np.linspace(0, 2 * np.pi, 160)
    radio = float(request.args.get("radio", 2.0))
    z = 0.35 * np.sin(2 * theta)
    return jsonify({"orbit": {"x": (radio * np.cos(theta)).tolist(),
                               "y": (radio * np.sin(theta)).tolist(), "z": z.tolist()},
                    "vectors": [{"origin": [0, 0, 0], "value": [1, 1, 0.5], "name": "v"},
                                {"origin": [0, 0, 0], "value": [-0.5, 1, 0.2], "name": "F"}]})


@app.route("/api/historial", methods=["GET", "POST"])
def api_historial():
    """Guarda y consulta el historial en SQLite respetando la identidad y el rol."""
    try:
        with get_auth_db() as conn:
            if request.method == "POST":
                data = request.get_json(silent=True) or request.form
                result = str(data.get("result", "")).strip()
                section = str(data.get("section", "general")).strip() or "general"
                if not result:
                    return jsonify({"error": "El resultado no puede estar vacío."}), 400

                # La identidad viene de la sesión validada, nunca del navegador.
                conn.execute(
                    "INSERT INTO history (username, section, result) VALUES (?, ?, ?)",
                    (g.current_user, section, result),
                )
                return jsonify({"saved": True})

            requested_user = request.args.get("username", "").strip()
            if g.current_role == "admin":
                if requested_user:
                    rows = conn.execute(
                        "SELECT username, section, result, created_at FROM history "
                        "WHERE username = ? ORDER BY id DESC LIMIT 200",
                        (requested_user,),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT username, section, result, created_at FROM history "
                        "ORDER BY id DESC LIMIT 200"
                    ).fetchall()
            else:
                # Un usuario normal solo puede consultar su propio historial.
                rows = conn.execute(
                    "SELECT username, section, result, created_at FROM history "
                    "WHERE username = ? ORDER BY id DESC LIMIT 100",
                    (g.current_user,),
                ).fetchall()

            return jsonify({"history": [dict(row) for row in rows]})
    except Exception:
        app.logger.exception("Error al acceder al historial MySQL")
        return jsonify({"error": "No se ha podido acceder al historial."}), 503




@app.route("/", methods=["GET", "POST"])
@app.route("/sistemas", methods=["GET", "POST"])
@app.route("/fisica", methods=["GET", "POST"])
@app.route("/resto", methods=["GET", "POST"])
@app.route("/calculo", methods=["GET", "POST"])
@app.route("/ejercicios", methods=["GET", "POST"])
@app.route("/simulador", methods=["GET", "POST"])
@app.route("/laboratorio3d", methods=["GET", "POST"])
@app.route("/historial", methods=["GET", "POST"])
def index():
    result = None
    error = None
    plot_url = None
    form_values: dict[str, str] = {}
    errors: list[str] = []
    sistema_filas = 2
    sistema_columnas = 2
    sistema_metodo = "reduccion"
    sistema_mostrar = False
    sistema_valores = {}
    sistema_resultado = None
    route_sections = {
        "/": "sistemas", "/sistemas": "sistemas", "/fisica": "fisica",
        "/resto": "resto", "/calculo": "calculo", "/ejercicios": "ejercicios",
        "/simulador": "simulador", "/laboratorio3d": "laboratorio3d", "/historial": "historial"
    }
    active_section = route_sections.get(request.path, "sistemas")

    if request.method == "POST":
        section = request.form.get("section")
        form_values = request.form.to_dict(flat=True)
        if section == 'fisica':
            active_section = 'fisica'

        elif section == 'sistema':
            active_section = 'sistemas'

        elif section in {
            'determinante',
            'inversa',
            'eigen',
            'vector',
            'calculo'
        }:
            active_section = 'calculo' if section == 'calculo' else 'resto'
        errors: list[str] = []

        if section == "sistema":
            try:
                sistema_filas = int(request.form.get("filas", 2))
                sistema_columnas = int(request.form.get("columnas", 2))
                if not 1 <= sistema_filas <= 8 or not 1 <= sistema_columnas <= 8:
                    raise ValueError("Las dimensiones deben estar entre 1 y 8.")
                sistema_metodo = request.form.get("metodo", "reduccion")
                sistema_mostrar = True
                sistema_valores = request.form.to_dict(flat=True)
                if request.form.get("accion") == "resolver":
                    coeficientes, independientes = convertir_formulario(request.form, sistema_filas, sistema_columnas)
                    resultado = analizar_sistema(coeficientes, independientes, sistema_metodo)
                    sistema_resultado = (
                        f"Tipo: {resultado['tipo']}\n"
                        f"Rango de A: {resultado['rango_matriz']}\n"
                        f"Rango de [A|b]: {resultado['rango_ampliada']}\n\n"
                        f"Solucion general: {resultado['solucion_general']}\n\n"
                        f"Forma reducida:\n{resultado['reducida']}\n\n"
                        f"Pasos:\n{'\n\n'.join(resultado['pasos'])}"
                    )
            except Exception as exc:
                error = str(exc)
                result = f"Error al procesar el sistema: {exc}"

        else:
            try:
                if section == "determinante":
                    matriz = parse_matrix_2x2(request.form)
                    det, pasos = calcular_determinante(matriz)
                    result = (
                        f"Determinante: {det}\n\n"
                        + "Matriz:\n" + np.array2string(matriz, precision=4, suppress_small=False) + "\n\n"
                        + "Pasos:\n" + "\n".join(pasos)
                    )
                elif section == "inversa":
                    matriz = parse_matrix_2x2(request.form)
                    inv, pasos = inversa_matriz(matriz)
                    result = (
                        f"Inversa:\n{np.array2string(inv, precision=4)}\n\n"
                        + "Comprobacion: A·A⁻¹ = I\n"
                        + np.array2string(matriz @ inv, precision=4) + "\n\n"
                        + "Pasos:\n" + "\n".join(pasos)
                    )
                elif section == "eigen":
                    matriz = parse_matrix_2x2(request.form)
                    vals, vecs, checks = autovalores_autovectores(matriz)
                    lines = [f"Autovalores: {vals}"]
                    for item in checks:
                        lines.append(
                            f"λ{item['indice']}: {item['autovalor']} | "
                            f"cumple Av = λv: {item['cumple']}"
                        )
                    result = "\n".join(lines)
                elif section == "vector":
                    u = parse_vector_3d(request.form)
                    ang = float(request.form.get("ang", 0.0))
                    rot = matriz_rotacion_2d(ang)
                    v = transformar_vector(np.array([u[0], u[1]], dtype=float), rot)
                    dot = producto_escalar(u[:2], v)
                    cross = producto_vectorial(np.array([1.0, 0.0, 0.0]), u)
                    result = (
                        f"Vector original: {u}\n"
                        f"Vector transformado (rotacion 2D): {v}\n"
                        f"Producto escalar: {dot}\n"
                        f"Producto vectorial e1 x u: {cross}"
                    )
                elif section == "calculo":
                    expr = request.form.get("expr", "x**2")
                    a = float(request.form.get("a", 0.0))
                    b = float(request.form.get("b", 1.0))
                    if not (a < b):
                        raise ValueError("El intervalo debe cumplir a < b.")

                    x_sym = symbols("x")
                    parsed = parse_expr(
                        expr,
                        local_dict={
                            "x": x_sym,
                            "sin": sin,
                            "cos": cos,
                            "tan": tan,
                            "exp": exp,
                            "log": log,
                            "sqrt": sqrt,
                            "pi": pi,
                            "e": EULER,
                            "abs": abs,
                        },
                        transformations=(standard_transformations + (implicit_multiplication_application,)),
                        evaluate=True,
                    )
                    if parsed.free_symbols - {x_sym}:
                        raise ValueError("Solo se permite la variable x y funciones matematicas seguras.")

                    f = lambda value: float(parsed.subs(x_sym, value).evalf())
                    deriv = derivada_numerica(f, (a + b) / 2)
                    integral = integrar_numerica(f, a, b)
                    result = f"Funcion: {expr}\nDerivada en x={(a + b)/2}: {deriv}\nIntegral en [{a},{b}]: {integral}"
                elif section == "fisica":
                    tool = request.form.get("tool", "proyectil")
                    if tool == "proyectil":
                        v0, err = parse_float_field(request.form, "v0", 20.0, required=True, min_val=0)
                        if err:
                            errors.append(err)
                        ang, err = parse_float_field(request.form, "angulo", 45.0, required=True)
                        if err:
                            errors.append(err)
                        g, err = parse_float_field(request.form, "g", 9.81, required=True, min_val=0)
                        if err:
                            errors.append(err)
                        tmax, err = parse_float_field(request.form, "tmax", 5.0, required=True, min_val=0)
                        if err:
                            errors.append(err)
                        if errors:
                            result = None
                        else:
                            datos = simulacion_proyectil(v0=v0, angulo_deg=ang, g=g, tiempo_max=tmax)
                            # generar grafica x vs y
                            try:
                                fig, ax = plt.subplots(figsize=(6,4), dpi=100, constrained_layout=True
                                )
                                ax.plot(datos['x'], datos['y'], '-o', markersize=3)
                                ax.set_xlabel('x (m)')
                                ax.set_ylabel('y (m)')
                                ax.set_title(f'Tiro parabólico v0={v0}, ang={ang}°')
                                ax.grid(True, alpha=0.3)
                                buf = io.BytesIO()
                                fig.savefig(buf, format='png', bbox_inches='tight')
                                buf.seek(0)
                                plot_url = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('ascii')
                                plt.close(fig)
                            except Exception:
                                plot_url = None
                            result = (
                                f"Proyectil: v0={v0}, ang={ang} deg, g={g}\n"
                                f"Alcance: {datos['alcance']:.6g}\n"
                                f"Altura maxima: {datos['altura_maxima']:.6g}\n"
                                f"Punto final: ({datos['x'][-1]:.6g}, {datos['y'][-1]:.6g})\n"
                                f"Muestra primeros 5 puntos:\n" + "\n".join([f"({x:.3f},{y:.3f})" for x, y in datos['trayectoria'][:5]])
                            )
                    elif tool == "caida":
                        h0, err = parse_float_field(request.form, "h0", 1.0, required=True)
                        if err: errors.append(err)
                        g, err = parse_float_field(request.form, "g", 9.81, required=True, min_val=0)
                        if err: errors.append(err)
                        if errors:
                            result = None
                        else:
                            datos = caida_libre(h0, g=g)
                            # generar grafica altura vs tiempo
                            try:
                                tmax_local = float(datos.get('tiempo', 0) or 0)
                                tarr = np.linspace(0, tmax_local if tmax_local>0 else 1, 200)
                                yarr = np.maximum(0, h0 - 0.5 * g * tarr ** 2)
                                fig, ax = plt.subplots(figsize=(6,4), dpi=100, constrained_layout=True)
                                ax.plot(tarr, yarr, '-b')
                                ax.set_xlabel('t (s)')
                                ax.set_ylabel('altura (m)')
                                ax.set_title(f'Caida libre h0={h0} m')
                                ax.grid(True, alpha=0.3)
                                buf = io.BytesIO()
                                fig.savefig(buf, format='png', bbox_inches='tight')
                                buf.seek(0)
                                plot_url = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('ascii')
                                plt.close(fig)
                            except Exception:
                                plot_url = None
                            result = f"Caida libre desde h0={h0}: tiempo={datos['tiempo']:.6g}s, velocidad={datos['velocidad_final']:.6g} m/s"
                    elif tool == "mru":
                        x0, err = parse_float_field(request.form, "x0", 0.0, required=True)
                        if err: errors.append(err)
                        v0, err = parse_float_field(request.form, "v0", 1.0, required=True)
                        if err: errors.append(err)
                        t, err = parse_float_field(request.form, "t", 1.0, required=True, min_val=0)
                        if err: errors.append(err)
                        if errors:
                            result = None
                        else:
                            # generar grafica x vs t
                            tarr = np.linspace(0, t, 200)
                            xarr = x0 + v0 * tarr
                            try:
                                fig, ax = plt.subplots(figsize=(6,4), dpi=100, constrained_layout=True)
                                ax.plot(tarr, xarr, '-o', markersize=3)
                                ax.set_xlabel('t (s)')
                                ax.set_ylabel('x (m)')
                                ax.set_title(f'MRU x0={x0}, v0={v0}')
                                ax.grid(True, alpha=0.3)
                                buf = io.BytesIO()
                                fig.savefig(buf, format='png', bbox_inches='tight')
                                buf.seek(0)
                                plot_url = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('ascii')
                                plt.close(fig)
                            except Exception:
                                plot_url = None
                            result = f"MRU: x(t) = {movimiento_mru(x0, v0, t):.6g}"
                    elif tool == "mrua":
                        x0, err = parse_float_field(request.form, "x0", 0.0, required=True)
                        if err: errors.append(err)
                        v0, err = parse_float_field(request.form, "v0", 1.0, required=True)
                        if err: errors.append(err)
                        a, err = parse_float_field(request.form, "a", 0.0, required=True)
                        if err: errors.append(err)
                        t, err = parse_float_field(request.form, "t", 1.0, required=True, min_val=0)
                        if err: errors.append(err)
                        if errors:
                            result = None
                        else:
                            # generar grafica posicion y velocidad vs tiempo
                            tarr = np.linspace(0, t, 200)
                            xpos = x0 + v0 * tarr + 0.5 * a * tarr ** 2
                            varr = v0 + a * tarr
                            try:
                                fig, axes = plt.subplots(2,1, figsize=(8,6), dpi=120, tight_layout=True)
                                axes[0].plot(tarr, xpos, '-b')
                                axes[0].set_ylabel('x (m)')
                                axes[0].grid(True, alpha=0.3)
                                axes[1].plot(tarr, varr, '-r')
                                axes[1].set_ylabel('v (m/s)')
                                axes[1].set_xlabel('t (s)')
                                axes[1].grid(True, alpha=0.3)
                                buf = io.BytesIO()
                                fig.savefig(buf, format='png', bbox_inches='tight')
                                buf.seek(0)
                                plot_url = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('ascii')
                                plt.close(fig)
                            except Exception:
                                plot_url = None
                            r = movimiento_mrua(x0, v0, a, t)
                            result = f"MRUA: posicion={r['posicion']:.6g}, velocidad={r['velocidad']:.6g}"
                    elif tool == "lorentz":
                        q, err = parse_float_field(request.form, "q", 1.0, required=True)
                        if err: errors.append(err)
                        vx, err = parse_float_field(request.form, "vx", 0.0, required=True)
                        if err: errors.append(err)
                        vy, err = parse_float_field(request.form, "vy", 0.0, required=True)
                        if err: errors.append(err)
                        vz, err = parse_float_field(request.form, "vz", 0.0, required=True)
                        if err: errors.append(err)
                        Ex, err = parse_float_field(request.form, "Ex", 0.0, required=True)
                        if err: errors.append(err)
                        Ey, err = parse_float_field(request.form, "Ey", 0.0, required=True)
                        if err: errors.append(err)
                        Ez, err = parse_float_field(request.form, "Ez", 0.0, required=True)
                        if err: errors.append(err)
                        Bx, err = parse_float_field(request.form, "Bx", 0.0, required=True)
                        if err: errors.append(err)
                        By, err = parse_float_field(request.form, "By", 0.0, required=True)
                        if err: errors.append(err)
                        Bz, err = parse_float_field(request.form, "Bz", 0.0, required=True)
                        if err: errors.append(err)
                        if errors:
                            result = None
                        else:
                            F = fuerza_lorentz(q, [vx, vy, vz], [Ex, Ey, Ez], [Bx, By, Bz])
                            # grafica componentes de la fuerza
                            try:
                                comp = np.array(F, dtype=float)
                                fig, ax = plt.subplots(figsize=(5,3), dpi=100, constrained_layout=True)
                                ax.bar(['Fx','Fy','Fz'], comp)
                                ax.set_title('Componentes de la fuerza de Lorentz')
                                buf = io.BytesIO()
                                fig.savefig(buf, format='png', bbox_inches='tight')
                                buf.seek(0)
                                plot_url = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('ascii')
                                plt.close(fig)
                            except Exception:
                                plot_url = None
                            result = f"Fuerza de Lorentz: {F.tolist()}"
                    elif tool == "colision":
                        m1, err = parse_float_field(request.form, "m1", 1.0, required=True, min_val=0)
                        if err: errors.append(err)
                        v1, err = parse_float_field(request.form, "v1", 0.0, required=True)
                        if err: errors.append(err)
                        m2, err = parse_float_field(request.form, "m2", 1.0, required=True, min_val=0)
                        if err: errors.append(err)
                        v2, err = parse_float_field(request.form, "v2", 0.0, required=True)
                        if err: errors.append(err)
                        elastic = request.form.get("elastic", "on") == "on"
                        if errors:
                            result = None
                        else:
                            v1p, v2p = colision_unidimensional(m1, v1, m2, v2, elastic=elastic)
                            # grafica velocidades antes/despues
                            try:
                                labels = ['v1 before','v2 before','v1 after','v2 after']
                                values = [v1, v2, v1p, v2p]
                                fig, ax = plt.subplots(figsize=(6,3), dpi=100, constrained_layout=True)
                                ax.bar(labels, values, color=['#4c72b0','#dd8452','#55a868','#c44e52'])
                                ax.set_ylabel('velocidad (m/s)')
                                ax.set_title('Colision 1D')
                                buf = io.BytesIO()
                                fig.savefig(buf, format='png', bbox_inches='tight')
                                buf.seek(0)
                                plot_url = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('ascii')
                                plt.close(fig)
                            except Exception:
                                plot_url = None
                            result = f"Colision ({'elastica' if elastic else 'inelastica'}): v1'={v1p:.6g}, v2'={v2p:.6g}"
                    elif tool == "oscilador":
                        m, err = parse_float_field(request.form, "m", 1.0, required=True, min_val=0)
                        if err: errors.append(err)
                        k, err = parse_float_field(request.form, "k", 1.0, required=True, min_val=0)
                        if err: errors.append(err)
                        q0, err = parse_float_field(request.form, "q0", 1.0, required=True)
                        if err: errors.append(err)
                        v0, err = parse_float_field(request.form, "v0", 0.0, required=True)
                        if err: errors.append(err)
                        tmax, err = parse_float_field(request.form, "tmax", 6.283, required=True, min_val=0)
                        if err: errors.append(err)
                        try:
                            n = int(request.form.get("n", 201))
                            if n < 3:
                                errors.append("El numero de puntos 'n' debe ser al menos 3.")
                        except Exception:
                            errors.append("El campo 'n' debe ser un entero valido.")
                        if errors:
                            result = None
                        else:
                            t = np.linspace(0, tmax, n)
                            q, v = oscilador_armonico(m, k, q0, v0, t, method=request.form.get("method", "rk4"))
                            energia_total = 0.5 * m * v ** 2 + 0.5 * k * q ** 2
                            # generar grafica q(t) y energia
                            try:
                                fig, axes = plt.subplots(2,1, figsize=(8,6), dpi=120, tight_layout=True)
                                axes[0].plot(t, q, '-k')
                                axes[0].set_ylabel('q (m)')
                                axes[0].set_title('Oscilador armónico')
                                axes[0].grid(True, alpha=0.3)
                                axes[1].plot(t, energia_total, '-r')
                                axes[1].set_ylabel('E (J)')
                                axes[1].set_xlabel('t (s)')
                                axes[1].grid(True, alpha=0.3)
                                buf = io.BytesIO()
                                fig.savefig(buf, format='png', bbox_inches='tight')
                                buf.seek(0)
                                plot_url = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('ascii')
                                plt.close(fig)
                            except Exception:
                                plot_url = None
                            result = f"Oscilador: energia var = {energia_total.max()-energia_total.min():.6g}\nPrimeros tres q: {q[:3].tolist()}"
                    elif tool == "doble_pendulo":
                        # simple small interface: take initial angles and return first/last state
                        th1, err = parse_float_field(request.form, "th1", 1.0, required=True)
                        if err: errors.append(err)
                        th2, err = parse_float_field(request.form, "th2", 1.0, required=True)
                        if err: errors.append(err)
                        w1, err = parse_float_field(request.form, "w1", 0.0, required=True)
                        if err: errors.append(err)
                        w2, err = parse_float_field(request.form, "w2", 0.0, required=True)
                        if err: errors.append(err)
                        L1, err = parse_float_field(request.form, "L1", 1.0, required=True, min_val=1e-6)
                        if err: errors.append(err)
                        L2, err = parse_float_field(request.form, "L2", 1.0, required=True, min_val=1e-6)
                        if err: errors.append(err)
                        m1, err = parse_float_field(request.form, "m1", 1.0, required=True, min_val=0)
                        if err: errors.append(err)
                        m2, err = parse_float_field(request.form, "m2", 1.0, required=True, min_val=0)
                        if err: errors.append(err)
                        tmax, err = parse_float_field(request.form, "tmax", 10.0, required=True, min_val=0)
                        if err: errors.append(err)
                        try:
                            n = int(request.form.get("n", 501))
                            if n < 10:
                                errors.append("El numero de puntos 'n' debe ser al menos 10.")
                        except Exception:
                            errors.append("El campo 'n' debe ser un entero valido.")
                        if errors:
                            result = None
                        else:
                            t = np.linspace(0, tmax, n)
                            thetas, omegas = doble_pendulo((th1, th2), (w1, w2), L1, L2, m1, m2, t)
                            # generar trayectoria x-y para ambas masas
                            try:
                                th1_arr = thetas[:,0]
                                th2_arr = thetas[:,1]
                                x1 = L1 * np.sin(th1_arr)
                                y1 = -L1 * np.cos(th1_arr)
                                x2 = x1 + L2 * np.sin(th2_arr)
                                y2 = y1 - L2 * np.cos(th2_arr)
                                fig, ax = plt.subplots(figsize=(6,5), dpi=100, constrained_layout=True)
                                ax.plot(x1, y1, '-b', label='masa1')
                                ax.plot(x2, y2, '-r', label='masa2')
                                ax.set_xlabel('x (m)')
                                ax.set_ylabel('y (m)')
                                ax.set_title('Trayectorias doble péndulo')
                                ax.legend()
                                ax.grid(True, alpha=0.3)
                                buf = io.BytesIO()
                                fig.savefig(buf, format='png', bbox_inches='tight')
                                buf.seek(0)
                                plot_url = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('ascii')
                                plt.close(fig)
                            except Exception:
                                plot_url = None
                            result = f"Doble pendulo: theta0=({th1},{th2}) -> theta_final=({thetas[-1,0]:.6g},{thetas[-1,1]:.6g})"
                    else:
                        result = "Herramienta de física no reconocida."
                else:
                    raise ValueError("Seccion no valida.")
            except Exception as exc:
                error = str(exc)
                result = f"Error: {exc}"

    # Registra automáticamente las operaciones enviadas desde los formularios clásicos.
    if request.method == "POST" and request.form.get("section") and result and not error and not str(result).startswith("Error"):
        section_key = request.form.get("section", "general")
        tool_name = request.form.get("tool", section_key)
        log_operation(section_key, tool_name, request.form.to_dict(flat=True), str(result))

    return render_template(
        "index.html",
        result=result,
        error=error,
        form_values=form_values,
        errors=errors,
        plot_url=plot_url,
        active_section=active_section,
        current_user=session.get("username"),
        user_role=session.get("role", "user"),
        sistema_filas=sistema_filas,
        sistema_columnas=sistema_columnas,
        sistema_metodo=sistema_metodo,
        sistema_mostrar=sistema_mostrar,
        sistema_valores=sistema_valores,
        sistema_resultado=sistema_resultado,
    )



@app.route('/download_plot', methods=['POST'])
def download_plot():
    """Recibe un data URI ('data:image/png;base64,...') en el campo 'imgdata' y lo devuelve como descarga.
    """
    imgdata = request.form.get('imgdata')
    if not imgdata:
        return "Imagen no encontrada", 400
    if ',' in imgdata:
        _hdr, b64 = imgdata.split(',', 1)
    else:
        b64 = imgdata
    try:
        data = base64.b64decode(b64)
    except Exception:
        return "Dato de imagen invalido", 400
    buf = io.BytesIO(data)
    buf.seek(0)
    # Intentar usar send_file con nombre de descarga moderno
    try:
        return send_file(buf, mimetype='image/png', as_attachment=True, download_name='plot.png')
    except TypeError:
        # Fallback para versiones antiguas de Flask
        return send_file(buf, mimetype='image/png', as_attachment=True, attachment_filename='plot.png')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
