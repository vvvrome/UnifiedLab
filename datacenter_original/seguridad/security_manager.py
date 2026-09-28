from seguridad.firewall import Firewall
from seguridad.policies import (
    SecurityPolicy,
    SecurityZone
)
from seguridad.ids import IntrusionDetectionSystem

class SecurityManager:

    def __init__(self):

        self.firewall = Firewall(
            "OT-FW-01"
        )

        self.ids = IntrusionDetectionSystem()

        self.events = []

        self._create_default_policies()
        

    # =========================
    # POLÍTICAS
    # =========================

    def _create_default_policies(self):

        # DMZ -> OT
        self.firewall.add_rule(
            SecurityPolicy(
                SecurityZone.DMZ,
                SecurityZone.OT,
                "TCP",
                443,
                "ALLOW"
            )
        )

        # OT -> CONTROL
        self.firewall.add_rule(
            SecurityPolicy(
                SecurityZone.OT,
                SecurityZone.CONTROL,
                "TCP",
                502,
                "ALLOW"
            )
        )


    # =========================
    # COMPROBAR CONEXIÓN
    # =========================

    def check_connection(
        self,
        source,
        destination,
        protocol,
        port
    ):

        action = self.firewall.check_connection(
            source.zone,
            destination.zone,
            protocol,
            port
        )

        ids_result = self.ids.inspect_connection(
            source,
            destination,
            protocol,
            port
        )


        if action == "DENY":

            self.create_security_event(
                source,
                destination,
                protocol,
                port
            )


        return action


    # =========================
    # EVENTO DE SEGURIDAD
    # =========================

    def create_security_event(
        self,
        source,
        destination,
        protocol,
        port
    ):

        event = {
            "timestamp": __import__(
                "datetime"
            ).datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "severity": "SECURITY",

            "type": "FIREWALL_DENY",

            "source": source.name,

            "source_zone": source.zone,

            "source_rack": source.rack.name,

            "destination": destination.name,

            "destination_zone":
                destination.zone,

            "destination_rack": destination.rack.name,

            "protocol": protocol,

            "port": port,

            "action": "DENY",

            "message": (
                f"Connection blocked: "
                f"{source.name} "
                f"({source.zone}) -> "
                f"{destination.name} "
                f"({destination.zone}) "
                f"{protocol}/{port}"
            )
        }

        self.events.append(
            event
        )


    # =========================
    # OBTENER EVENTOS
    # =========================

    def get_events(self):

        return (self.events + self.ids.get_events())