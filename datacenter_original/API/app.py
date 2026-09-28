import os
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from functools import wraps


def create_app(
    datacenter,
    alert_manager,
    security_manager,
    plant,
    create_user
):

    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(32)
    app.config["SESSION_PERMANENT"] = False
    from database.users import (
        authenticate_user,
        create_user,
        get_all_users,
        get_user_by_username
    )
    from database.audit import log_event, get_audit_logs


    def login_required(role=None):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):

                username = session.get("username")

                if not username:
                    return redirect(url_for("login"))

                user = get_user_by_username(username)

                if user is None:
                    session.clear()
                    return redirect(url_for("login"))

                if role and user["role"] != role:
                    return "Acceso denegado", 403

                return f(*args, **kwargs)

            return wrapper
        return decorator
    
    def audit(
        username,
        action,
        result,
        details=None
    ):

        log_event(
            username=username,
            action=action,
            result=result,
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            details=details
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():

        if request.method == "POST":

            username = request.form.get(
                "username",
                ""
            ).strip()

            password = request.form.get(
                "password",
                ""
            )

            user = authenticate_user(
                username,
                password
            )

            if user:

                session.clear()

                session.permanent = False

                session["username"] = user["username"]
                session["role"] = user["role"]

                audit(
                    username,
                    "LOGIN",
                    "SUCCESS"
                )

                return redirect(
                    url_for("index")
                )

            audit(
                username or "UNKNOWN",
                "LOGIN",
                "FAILED",
                "Invalid credentials"
            )

            return render_template(
                "login.html",
                error="Usuario o contraseña incorrectos"
            )

        # GET /login: mostrar el formulario. Sin este return, Flask recibe None.
        return render_template("login.html")

    @app.route("/logout")
    def logout():

        username = session.get(
            "username",
            "UNKNOWN"
        )

        audit(
            username,
            "LOGOUT",
            "SUCCESS"
        )

        session.clear()

        return redirect(
            url_for("login")
        )

    @app.route("/register", methods=["GET", "POST"])
    def register():

        if request.method == "POST":

            username = request.form.get(
                "username",
                ""
            ).strip()

            password = request.form.get(
                "password",
                ""
            )

            password_confirm = request.form.get(
                "password_confirm",
                ""
            )

            if not username or not password:

                return render_template(
                    "register.html",
                    error="Todos los campos son obligatorios."
                )

            if password != password_confirm:

                return render_template(
                    "register.html",
                    error="Las contraseñas no coinciden."
                )

            if len(username) < 3:

                return render_template(
                    "register.html",
                    error="El usuario debe tener al menos 3 caracteres."
                )

            if len(password) < 8:

                return render_template(
                    "register.html",
                    error="La contraseña debe tener al menos 8 caracteres."
                )

            created = create_user(
                username,
                password,
                "VIEWER"
            )

            if created:
                audit(
                    username,
                    "REGISTER",
                    "SUCCESS",
                    "New VIEWER account created"
                )

            if not created:

                return render_template(
                    "register.html",
                    error="Ese usuario ya existe."
                )

            return redirect(
                url_for("login")
            )

        return render_template(
            "register.html"
        )

    @app.route("/")
    @login_required()
    def index():

        return render_template(
            "index.html"
        )

    @app.route("/admin/users")
    @login_required(role="ADMIN")
    def admin_users():

        audit(
            session.get("username"),
            "ACCESS_ADMIN_USERS",
            "SUCCESS"
        )
        
        users = get_all_users()

        return render_template(
            "admin_users.html",
            users=users
        )

    @app.route("/admin/audit")
    @login_required(role="ADMIN")
    def admin_audit():

        audit(
            session.get("username"),
            "ACCESS_AUDIT_LOG",
            "SUCCESS"
        )

        logs = get_audit_logs()

        return render_template(
            "admin_audit.html",
            logs=logs
        )
    
    @app.route("/api/status")
    @login_required()
    def status():

        data = {
            "name": datacenter.name,
            "racks": []
        }


        for rack in datacenter.racks:

            rack_data = {

                "name": rack.name,

                "total_units":
                    rack.total_units,

                "used_units":
                    rack.used_units(),

                "available_units":
                    rack.available_units(),

                "servers": [],

                "switches": [],

                "routers": []

            }


            # =========================
            # SERVIDORES
            # =========================

            for server in rack.servers:

                server_data = {

                    "name": server.name,

                    "type":
                        server.server_type,

                    "status":
                        server.status,

                    "cpu":
                        server.cpu_usage,

                    "ram":
                        server.ram_usage,

                    "network":
                        server.network_usage,

                    "temperature":
                        server.temperature,

                    "power":
                        server.power_consumption,

                    "switch":
                        server.switch,

                    "switch_port":
                        server.switch_port

                }

                rack_data[
                    "servers"
                ].append(
                    server_data
                )


            # =========================
            # SWITCHES
            # =========================

            for switch in rack.switches:

                switch_data = {

                    "name":
                        switch.name,

                    "ports":
                        switch.ports,

                    "used_ports":
                        switch.get_used_ports(),

                    "available_ports":
                        switch.get_available_ports(),

                    "traffic":
                        switch.traffic_usage,

                    "temperature":
                        switch.temperature,

                    "power":
                        switch.power_consumption,

                    "status":
                        switch.status,

                    "ports_status":
                        switch.get_ports_status()

                }

                rack_data[
                    "switches"
                ].append(
                    switch_data
                )


            # =========================
            # ROUTERS
            # =========================

            for router in rack.routers:

                router_data = {

                    "name":
                        router.name,

                    "ports":
                        router.ports,

                    "used_ports":
                        router.get_used_ports(),

                    "available_ports":
                        router.get_available_ports(),

                    "traffic":
                        router.traffic_usage,

                    "temperature":
                        router.temperature,

                    "power":
                        router.power_consumption,

                    "status":
                        router.status,

                    "ports_status":
                        router.get_ports_status()

                }

                rack_data[
                    "routers"
                ].append(
                    router_data
                )


            data[
                "racks"
            ].append(
                rack_data
            )


        return jsonify(data)


    # =========================
    # ALERTAS NORMALES
    # =========================

    @app.route("/api/alerts")
    @login_required()
    def alerts():

        return jsonify(
            alert_manager.get_alerts()
        )


    # ========================================
    # QKD - EJECUTAR SESIÓN
    # ========================================

    @app.route("/api/plant/qkd/session", methods=["POST"])
    @login_required(role="ADMIN")
    def qkd_session():

        data = request.get_json(silent=True) or {}

        eve = data.get("eve", False)

        result = plant.run_qkd_session(
            eve=eve
        )

        audit(
            session.get("username"),
            "QKD_SESSION",
            result.get("status", "UNKNOWN"),
            f"Eve={eve}, QBER={result.get('qber_percent')}"
        )

        # Una sesión comprometida debe quedar registrada como
        # alerta de seguridad de la planta.
        if result.get("status") == "COMPROMISED":
            plant.alert_manager.add_alert(
                severity="CRITICAL",
                message=(
                    "QKD session compromised: possible interception detected"
                ),
                device="QKD-01",
                parameter="QBER",
                value=result.get("qber_percent")
            )

        return jsonify(result)

    # =========================
    # EVENTOS DE SEGURIDAD
    # =========================

    @app.route("/api/security/events")
    @login_required()
    def security_events():

        return jsonify(
            security_manager.get_events()
        )


    @app.route("/api/plant")
    @login_required()
    def plant_status():

        return jsonify(
            plant.get_state()
        )

    @app.route("/api/plant/alerts")
    @login_required()
    def plant_alerts():

        return jsonify(
            plant.alert_manager.get_alerts()
        )

    @app.route("/plant")
    @login_required()
    def plant_page():

        return render_template(
            "plant.html"
        )

    return app