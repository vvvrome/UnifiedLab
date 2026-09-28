import random
import time


class FaultManager:

    def __init__(
        self,
        plant,
        config=None
    ):

        self.plant = plant

        config = config or {}

        self.enabled = config.get(
            "enabled",
            True
        )

        self.check_interval = config.get(
            "check_interval",
            10
        )

        self.sensor_probability = config.get(
            "sensor_failure_probability",
            0.02
        )

        self.actuator_probability = config.get(
            "actuator_failure_probability",
            0.01
        )

        self.min_duration = config.get(
            "min_duration",
            5
        )

        self.max_duration = config.get(
            "max_duration",
            15
        )

        self.last_check = time.time()

        self.active_fault = None


    def update(self):

        if not self.enabled:
            return


        now = time.time()


        # ==================================
        # COMPROBAR FALLO ACTIVO
        # ==================================

        if self.active_fault:

            if now >= self.active_fault["end_time"]:

                self.recover_fault()

            return


        # ==================================
        # ESPERAR SIGUIENTE COMPROBACIÓN
        # ==================================

        if (
            now - self.last_check
            < self.check_interval
        ):

            return


        self.last_check = now


        # ==================================
        # DECIDIR SI OCURRE UN FALLO
        # ==================================

        if (
            random.random()
            < self.sensor_probability
        ):

            self.create_sensor_fault()

            return


        if (
            random.random()
            < self.actuator_probability
        ):

            self.create_actuator_fault()


    def create_sensor_fault(self):

        available = [

            sensor

            for sensor in self.plant.sensors

            if not sensor.failed

        ]


        if not available:
            return


        sensor = random.choice(
            available
        )


        duration = random.uniform(
            self.min_duration,
            self.max_duration
        )


        sensor.failed = True

        self.plant.alert_manager.add_alert(
            severity="WARNING",
            message=(
                f"Sensor failure detected: "
                f"{sensor.name}"
            ),
            device=sensor.name,
            parameter=sensor.parameter,
            value=sensor.value
        )

        self.active_fault = {

            "type":
                "SENSOR_FAILURE",

            "device":
                sensor,

            "device_name":
                sensor.name,

            "start_time":
                time.time(),

            "end_time":
                time.time() + duration

        }


        print(
            f"[FAULT] SENSOR FAILURE: "
            f"{sensor.name}"
        )


    def create_actuator_fault(self):

        available = [

            actuator

            for actuator in self.plant.actuators

            if not actuator.failed

        ]


        if not available:

            return


        actuator = random.choice(
            available
        )


        duration = random.uniform(
            self.min_duration,
            self.max_duration
        )


        actuator.failed = True


        self.active_fault = {

            "type":
                "ACTUATOR_FAILURE",

            "device":
                actuator,

            "device_name":
                actuator.name,

            "start_time":
                time.time(),

            "end_time":
                time.time() + duration

        }


        self.plant.alert_manager.add_alert(

            severity="WARNING",

            message=(
                f"Actuator failure detected: "
                f"{actuator.name}"
            ),

            device=actuator.name,

            parameter=actuator.parameter

        )


        print(
            f"[FAULT] ACTUATOR FAILURE: "
            f"{actuator.name}"
        )


    def recover_fault(self):

        fault = self.active_fault


        if not fault:
            return


        device = fault["device"]


        device.failed = False

        self.plant.alert_manager.add_alert(
            severity="INFO",
            message=f"Device recovered: {device.name}",
            device=device.name
        )

        print(
            f"[FAULT RECOVERED] "
            f"{fault['type']}: "
            f"{fault['device_name']}"
        )


        self.active_fault = None