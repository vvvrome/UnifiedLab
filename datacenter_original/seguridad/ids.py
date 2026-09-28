from datetime import datetime


class IntrusionDetectionSystem:

    def __init__(self):

        self.events = []

        self.connection_history = {}

        self.thresholds = {
            "WARNING": 10,
            "CRITICAL": 25
        }


    def inspect_connection(
        self,
        source,
        destination,
        protocol,
        port
    ):

        key = (
            source.name,
            destination.name,
            protocol,
            port
        )

        self.connection_history[key] = (
            self.connection_history.get(
                key,
                0
            ) + 1
        )

        count = self.connection_history[key]


        # =========================
        # CRITICAL
        # =========================

        if count >= self.thresholds["CRITICAL"]:

            self.create_event(
                source,
                destination,
                protocol,
                port,
                "CRITICAL",
                count
            )

            return "CRITICAL"


        # =========================
        # WARNING
        # =========================

        if count >= self.thresholds["WARNING"]:

            self.create_event(
                source,
                destination,
                protocol,
                port,
                "WARNING",
                count
            )

            return "WARNING"


        return "NORMAL"


    def create_event(
        self,
        source,
        destination,
        protocol,
        port,
        severity,
        count
    ):

        event = {

            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "type":
                "IDS_ANOMALY",

            "severity":
                severity,

            "source":
                source.name,

            "source_zone":
                source.zone,

            "source_rack":
                source.rack.name,

            "destination":
                destination.name,

            "destination_zone":
                destination.zone,

            "destination_rack":
                destination.rack.name,

            "protocol":
                protocol,

            "port":
                port,

            "connection_count":
                count,

            "message": (
                f"Abnormal connection "
                f"pattern detected: "
                f"{source.name} -> "
                f"{destination.name} "
                f"{protocol}/{port} "
                f"({count} connections)"
            )
        }

        self.events.append(event)


    def get_events(self):

        return self.events