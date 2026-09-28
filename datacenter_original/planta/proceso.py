from planta.reactor import Reactor
from planta.sensores import Sensor
from planta.actuadores import Actuator
from planta.controlador import PlantController
from collections import deque
from planta.fault_manager import FaultManager
from planta.safety_controller import SafetyController
from planta.alert_manager import PlantAlertManager
from planta.security.qkd_manager import QKDManager
from planta.security.security_controller import SecurityController


class NuclearPlant:

    def __init__(self, fault_config=None    ):

        self.reactor = Reactor(
            "REACTOR-01"
        )

        self.controller = PlantController(
            self.reactor
        )

        self.sensors = []

        self.actuators = []

        self.history = {

            "labels": deque(maxlen=60),

            "temperature": deque(maxlen=60),

            "power": deque(maxlen=60),

            "coolant_flow": deque(maxlen=60)

        }

        self._create_sensors()

        self._create_actuators()

        self.fault_manager = FaultManager(
            self,
            fault_config
        )

        self.safety_controller = SafetyController(
            self
        )

        self.alert_manager = PlantAlertManager()

        self.qkd_manager = QKDManager(
            key_length=256,
            qber_threshold=0.11,
            alert_manager=self.alert_manager
        )

        self.security_controller = SecurityController(
            self.alert_manager
        )

        self.qkd_manager.start_session(
            eve=False
        )

        

    # =========================
    # SENSORES
    # =========================

    def _create_sensors(self):

        self.sensors = [

            Sensor(
                "TEMP-01",
                "temperature",
                self.reactor
            ),

            Sensor(
                "TEMP-02",
                "temperature",
                self.reactor
            ),

            Sensor(
                "PRESSURE-01",
                "pressure",
                self.reactor
            ),

            Sensor(
                "FLOW-01",
                "coolant_flow",
                self.reactor
            ),

            Sensor(
                "POWER-01",
                "power",
                self.reactor
            ),

            Sensor(
                "LEVEL-01",
                "water_level",
                self.reactor
            ),

            Sensor(
                "RADIATION-01",
                "radiation",
                self.reactor
            )

        ]


    # =========================
    # ACTUADORES
    # =========================

    def _create_actuators(self):

        self.actuators = [

            Actuator(
                "COOLANT-PUMP-01",
                "coolant_flow",
                self.reactor
            ),

            Actuator(
                "POWER-CONTROL-01",
                "power",
                self.reactor
            )

        ]

        self.reactor.actuators = self.actuators
    def update(self):

        # =========================
        # FALLOS ALEATORIOS
        # =========================

        self.fault_manager.update()


        # =========================
        # PROCESO
        # =========================

        self.reactor.update()


        # =========================
        # SENSORES
        # =========================

        for sensor in self.sensors:

            sensor.read()


        # =========================
        # CONTROL NORMAL
        # =========================

        self.controller.update()


        # =========================
        # SEGURIDAD
        # =========================

        self.safety_controller.update()


        # =========================
        # HISTORIAL
        # =========================

        from datetime import datetime

        self.history["labels"].append(
            datetime.now().strftime(
                "%H:%M:%S"
            )
        )

        self.history["temperature"].append(
            self.reactor.temperature
        )

        self.history["power"].append(
            self.reactor.power
        )

        self.history["coolant_flow"].append(
            self.reactor.coolant_flow
        )

    # =========================
    # ESTADO
    # =========================

    def get_state(self):

        return {

            "reactor":
                self.reactor.get_state(),

            "controller":
                self.controller.get_state(),

            "safety":
                self.safety_controller.get_state(),

            "qkd":
                self.qkd_manager.get_status(),

            "security":
                self.security_controller.get_state(),

            "sensors": [

                sensor.get_data()

                for sensor in self.sensors

            ],

            "actuators": [

                actuator.get_data()

                for actuator in self.actuators

            ],

            "history": {

                "labels":
                    list(
                        self.history["labels"]
                    ),

                "temperature":
                    list(
                        self.history["temperature"]
                    ),

                "power":
                    list(
                        self.history["power"]
                    ),

                "coolant_flow":
                    list(
                        self.history["coolant_flow"]
                    )

            }

        }

    def set_sensor_status(
        self,
        sensor_name,
        status
    ):

        for sensor in self.sensors:

            if sensor.name == sensor_name:

                sensor.set_status(
                    status
                )

                return True

        return False

    def set_actuator_status(
        self,
        actuator_name,
        status
    ):

        for actuator in self.actuators:

            if actuator.name == actuator_name:

                actuator.set_status(
                    status
                )

                return True

        return False

    def run_qkd_session(self, eve=False):

        result = self.qkd_manager.start_session(
            eve=eve
        )

        self.security_controller.handle_qkd_result(
            result
        )

        return result