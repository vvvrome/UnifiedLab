class PlantController:

    def __init__(self, reactor):

        self.reactor = reactor

        self.mode = "AUTO"

        self.status = "NORMAL"


    def update(self):

        if self.mode != "AUTO":

            return


        temperature = (
            self.reactor.temperature
        )


        # =========================
        # CONTROL DE REFRIGERACIÓN
        # =========================

        if temperature >= 320:

            self.reactor.coolant_flow += 2


        elif temperature >= 310:

            self.reactor.coolant_flow += 1


        elif temperature <= 290:

            self.reactor.coolant_flow -= 1


        # =========================
        # LIMITES
        # =========================

        self.reactor.coolant_flow = max(
            0,
            min(
                100,
                self.reactor.coolant_flow
            )
        )


        # =========================
        # ESTADO
        # =========================

        if temperature >= 340:

            self.status = "CRITICAL"

        elif temperature >= 320:

            self.status = "WARNING"

        else:

            self.status = "NORMAL"


    def get_state(self):

        return {

            "mode":
                self.mode,

            "status":
                self.status

        }