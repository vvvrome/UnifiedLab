class Sensor:

    def __init__(
        self,
        name,
        parameter,
        reactor
    ):

        self.name = name
        self.parameter = parameter
        self.reactor = reactor

        self.value = 0.0

        self.status = "ONLINE"

        self.failed = False

    def read(self):

        if self.failed:

            self.status = "FAILED"

            return self.value


        self.value = getattr(
            self.reactor,
            self.parameter
        )

        self.status = "ONLINE"

        return self.value


    def set_status(self, status):

        allowed = [
            "ONLINE",
            "DEGRADED",
            "OFFLINE",
            "MAINTENANCE"
        ]

        if status not in allowed:

            raise ValueError(
                f"Invalid sensor status: {status}"
            )

        self.status = status


    def get_data(self):

        return {

            "name":
                self.name,

            "parameter":
                self.parameter,

            "value":
                self.value
                if self.status != "OFFLINE"
                else None,

            "status":
                self.status

        }