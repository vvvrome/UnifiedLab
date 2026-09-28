class Actuator:

    def __init__(
        self,
        name,
        parameter,
        reactor
    ):

        self.name = name
        self.parameter = parameter
        self.reactor = reactor

        self.status = "ONLINE"

        self.failed = False

    def set_value(self, value):

        if self.failed:

            self.status = "FAILED"

            return False


        setattr(
            self.reactor,
            self.parameter,
            value
        )

        self.status = "READY"

        return True


    def set_status(self, status):

        allowed = [
            "ONLINE",
            "DEGRADED",
            "OFFLINE",
            "MAINTENANCE"
        ]

        if status not in allowed:

            raise ValueError(
                f"Invalid actuator status: {status}"
            )

        self.status = status


    def get_data(self):

        return {

            "name":
                self.name,

            "parameter":
                self.parameter,

            "status":
                self.status

        }