import random

class Reactor:

    def __init__(self, name):

        self.name = name

        # =========================
        # VARIABLES DEL PROCESO
        # =========================

        self.temperature = 300.0

        self.pressure = 150.0

        self.coolant_flow = 100.0

        self.power = 100.0

        self.water_level = 100.0

        self.radiation = 1.0

        self.status = "NORMAL"

        self.fault = None


    def update(self):

        import random


        # ==================================
        # VARIACIONES NATURALES DEL PROCESO
        # ==================================

        target_power = 100.0

        self.power += (
            target_power - self.power
        ) * 0.05

        self.power += random.uniform(
            -0.05,
            0.05
        )


        target_flow = 100.0

        self.coolant_flow += (
            target_flow - self.coolant_flow
        ) * 0.03

        self.coolant_flow += random.uniform(
            -0.10,
            0.10
        )


        # ==================================
        # EFECTOS DE FALLOS
        # ==================================

        cooling_failure = False
        power_failure = False


        # El reactor recibe los actuadores
        # mediante esta lista si está disponible.

        if hasattr(self, "actuators"):

            for actuator in self.actuators:

                if not actuator.failed:
                    continue


                if actuator.parameter == "coolant_flow":

                    cooling_failure = True


                elif actuator.parameter == "power":

                    power_failure = True


        # ==================================
        # FALLO DE BOMBA DE REFRIGERACIÓN
        # ==================================

        if cooling_failure:

            self.coolant_flow -= random.uniform(
                1.5,
                3.0
            )


        # ==================================
        # FALLO DEL CONTROL DE POTENCIA
        # ==================================

        if power_failure:

            self.power += random.uniform(
                -0.5,
                0.5
            )


        # ==================================
        # EFECTO DE LA POTENCIA
        # ==================================

        heat_generation = (
            self.power * 0.010
        )


        # ==================================
        # EFECTO DE LA REFRIGERACIÓN
        # ==================================

        cooling = (
            self.coolant_flow * 0.010
        )


        # ==================================
        # EVOLUCIÓN DE TEMPERATURA
        # ==================================

        temperature_change = (
            heat_generation -
            cooling
        )


        # Tendencia natural hacia
        # la temperatura de equilibrio.

        temperature_change += (
            300.0 - self.temperature
        ) * 0.02


        self.temperature += (
            temperature_change
        )


        # ==================================
        # PRESIÓN
        # ==================================

        self.pressure = (
            120.0 +
            self.temperature * 0.10
        )


        # ==================================
        # NIVEL DE AGUA
        # ==================================

        self.water_level -= (
            self.temperature - 300.0
        ) * 0.0005


        self.water_level += (
            self.coolant_flow - 100.0
        ) * 0.001


        # ==================================
        # RADIACIÓN
        # ==================================

        self.radiation = (
            1.0 +
            self.power * 0.005
        )


        # ==================================
        # LIMITES
        # ==================================

        self.temperature = max(
            0.0,
            self.temperature
        )


        self.pressure = max(
            0.0,
            self.pressure
        )


        self.coolant_flow = max(
            0.0,
            min(
                100.0,
                self.coolant_flow
            )
        )


        self.power = max(
            0.0,
            min(
                100.0,
                self.power
            )
        )


        self.water_level = max(
            0.0,
            min(
                100.0,
                self.water_level
            )
        )


        # ==================================
        # ESTADO DEL REACTOR
        # ==================================

        if self.temperature >= 340:

            self.status = "CRITICAL"

        elif self.temperature >= 320:

            self.status = "WARNING"

        else:

            self.status = "NORMAL"

    def get_state(self):

        return {

            "name":
                self.name,

            "temperature":
                self.temperature,

            "pressure":
                self.pressure,

            "coolant_flow":
                self.coolant_flow,

            "power":
                self.power,

            "water_level":
                self.water_level,

            "radiation":
                self.radiation,

            "status":
                self.status

        }