import threading
import time

from database.users import init_database, create_user
from database.audit import init_audit_database
init_database()
init_audit_database()
from infraestructura.datacenter import DataCenter
from simulacion.motor import SimulationEngine
from config.loader import load_config
from API.app import create_app
from infraestructura.switch import Switch
from infraestructura.router import Router


# =========================
# CONFIGURACIÓN
# =========================

config = load_config(
    "config/datacenter.yaml"
)

datacenter = DataCenter.from_config(
    config["datacenter"]
)

engine = SimulationEngine(
    datacenter,
    config
)


print(engine.plant.get_state())

# =========================
# CONFIGURAR RACKS
# =========================

def setup_rack(rack, rack_number):

    switch = Switch(
        name=f"SWITCH-{rack_number:02d}",
        ports=48
    )

    switch.rack = rack
    switch.zone = "OT"

    rack.add_switches(
        switch
    )

    router = Router(
        name=f"ROUTER-{rack_number:02d}",
        ports=8
    )

    router.rack = rack
    router.zone = "DMZ"

    rack.add_router(
        router
    )

    for server in rack.servers:

        server.rack = rack
        server.zone = "OT"

    for port, server in enumerate(
        rack.servers,
        start=1
    ):

        switch.connect_server(
            server,
            port
        )

    router.connect_device(
        switch,
        1
    )


# Configurar todos los racks
for index, rack in enumerate(
    datacenter.racks,
    start=1
):

    setup_rack(
        rack,
        index
    )


# =========================
# PRUEBA DE SEGURIDAD
# =========================

rack = datacenter.racks[0]

router = rack.routers[0]

server = rack.servers[0]

print(
    "ROUTER:",
    router.name,
    "ZONE:",
    router.zone
)

print(
    "SERVER:",
    server.name,
    "ZONE:",
    server.zone
)

result = engine.security_manager.check_connection(
    router,
    server,
    "TCP",
    443
)

print(
    "SECURITY TEST DMZ -> OT TCP 443:",
    result
)


result = engine.security_manager.check_connection(
    router,
    server,
    "TCP",
    22
)

print(
    "SECURITY TEST DMZ -> OT TCP 22:",
    result
)

print(
    "Security Events:"
)

for event in engine.security_manager.get_events():
    print(event)

print(
    "IDS TEST"
)

for i in range(12):

    result = engine.security_manager.check_connection(
        router,
        server,
        "TCP",
        443
    )

    print(
        i + 1,
        result
    )

# =========================
# SIMULACIÓN
# =========================

def run_simulation():

    last_alert_count = 0

    while True:

        engine.update()

        alerts = (
            engine.alert_manager.get_alerts()
        )

        if len(alerts) > last_alert_count:

            new_alerts = alerts[
                last_alert_count:
            ]

            for alert in new_alerts:
                print(alert)

            last_alert_count = len(alerts)

        time.sleep(1)


# =========================
# HILO DE SIMULACIÓN
# =========================

simulation_thread = threading.Thread(
    target=run_simulation,
    daemon=True
)

simulation_thread.start()


# =========================
# WEB
# =========================

app = create_app(
    datacenter,
    engine.alert_manager,
    engine.security_manager,
    engine.plant,
    create_user
)

app.run(
    debug=True,
    use_reloader=False,
    host="0.0.0.0",
    port=5000
)