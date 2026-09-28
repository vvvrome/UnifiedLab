class SecurityZone:

    IT = "IT"
    DMZ = "DMZ"
    OT = "OT"
    CONTROL = "CONTROL"
    SAFETY = "SAFETY"


class SecurityPolicy:

    def __init__(
        self,
        source_zone,
        destination_zone,
        protocol,
        port,
        action="DENY"
    ):

        self.source_zone = source_zone
        self.destination_zone = destination_zone
        self.protocol = protocol
        self.port = port
        self.action = action