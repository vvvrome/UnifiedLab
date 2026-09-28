class SafetyController:

    def __init__(self, plant):

        self.plant = plant

        self.status = "NORMAL"

        self.last_action = None

        self.previous_status = "NORMAL"

    def update(self):

        self.status = "NORMAL"

        self.last_action = None


        # ==================================
        # COMPROBAR SENSORES
        # ==================================

        failed_sensors = [

            sensor

            for sensor in self.plant.sensors

            if sensor.failed

        ]


        if failed_sensors:

            self.status = "WARNING"

            self.last_action = (
                "Sensor failure detected"
            )


        # ==================================
        # COMPROBAR ACTUADORES
        # ==================================

        failed_actuators = [

            actuator

            for actuator in self.plant.actuators

            if actuator.failed

        ]


        if failed_actuators:

            self.status = "WARNING"

            self.last_action = (
                "Actuator failure detected"
            )


        # ==================================
        # ESTADO DEL REACTOR
        # ==================================

        if (
            self.plant.reactor.status
            == "CRITICAL"
        ):

            self.status = "CRITICAL"

            self.last_action = (
                "Critical reactor condition"
            )

        if self.status != self.previous_status:

            self.plant.alert_manager.add_alert(

                severity=self.status,

                message=(
                    f"Safety state changed to "
                    f"{self.status}"
                )

            )

            self.previous_status = self.status

    def get_state(self):

        return {

            "status":
                self.status,

            "last_action":
                self.last_action

        }