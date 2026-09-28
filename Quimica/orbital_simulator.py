import numpy as np

from .stellar_physics import (
    G,
    MASA_SOL,
    RADIO_SOL
)


MASA_TIERRA = 5.9722e24
UA = 1.495978707e11


class OrbitalSimulator:
    def __init__(self, estrella, planetas):
        self.estrella = estrella
        self.planetas = planetas

        self.n = len(planetas) + 1

        self.masas = self._crear_masas()
        self.posiciones = self._crear_posiciones()
        self.velocidades = self._crear_velocidades()

    def _crear_masas(self):
        """Convierte masas solares y terrestres a kg."""

        masas = [
            self.estrella.masa * MASA_SOL
        ]

        for planeta in self.planetas:
            masas.append(planeta.masa * MASA_TIERRA)

        return np.array(masas, dtype=float)

    def _crear_posiciones(self):
        """
        Estrella en el origen.
        Planetas situados según su distancia orbital.
        """

        posiciones = np.zeros((self.n, 2), dtype=float)

        for i, planeta in enumerate(self.planetas, start=1):
            distancia = planeta.distancia * UA

            posiciones[i] = [
                distancia,
                0.0
            ]

        return posiciones

    def _crear_velocidades(self):
        """
        Velocidad tangencial inicial aproximada:
        v = sqrt(G*M/r)

        Es una aproximación de órbita circular.
        """

        velocidades = np.zeros((self.n, 2), dtype=float)

        masa_estrella = self.masas[0]

        for i, planeta in enumerate(self.planetas, start=1):
            radio_orbital = planeta.distancia * UA

            velocidad = np.sqrt(
                G * (masa_estrella + self.masas[i])
                / radio_orbital
            )

            velocidades[i] = [
                0.0,
                velocidad
            ]

        # Compensación para que el centro de masa
        # tenga velocidad total aproximadamente nula.
        momento = np.sum(
            self.masas[:, None] * velocidades,
            axis=0
        )

        velocidades[0] = -momento / self.masas[0]

        return velocidades

    def _aceleraciones(self, posiciones):
        """Calcula aceleraciones gravitatorias mutuas."""

        aceleraciones = np.zeros_like(posiciones)

        for i in range(self.n):
            for j in range(self.n):
                if i == j:
                    continue

                delta = posiciones[j] - posiciones[i]
                distancia = np.linalg.norm(delta)

                if distancia == 0:
                    raise ValueError(
                        "Dos cuerpos ocupan la misma posición."
                    )

                aceleraciones[i] += (
                    G * self.masas[j]
                    * delta / distancia**3
                )

        return aceleraciones

    def simular(self, tiempo_total, dt=3600):
        """
        Ejecuta la simulación mediante Velocity Verlet.

        tiempo_total: segundos
        dt: paso temporal en segundos
        """

        if tiempo_total <= 0:
            raise ValueError(
                "El tiempo total debe ser positivo."
            )

        if dt <= 0:
            raise ValueError(
                "El paso temporal debe ser positivo."
            )

        pasos = int(tiempo_total / dt)

        posiciones = self.posiciones.copy()
        velocidades = self.velocidades.copy()

        historial = []

        aceleraciones = self._aceleraciones(posiciones)

        for _ in range(pasos):
            historial.append(posiciones.copy())

            posiciones_nuevas = (
                posiciones
                + velocidades * dt
                + 0.5 * aceleraciones * dt**2
            )

            aceleraciones_nuevas = self._aceleraciones(
                posiciones_nuevas
            )

            velocidades += (
                0.5
                * (aceleraciones + aceleraciones_nuevas)
                * dt
            )

            posiciones = posiciones_nuevas
            aceleraciones = aceleraciones_nuevas

        self.posiciones = posiciones
        self.velocidades = velocidades

        return {
            "tiempo": tiempo_total,
            "dt": dt,
            "posiciones": np.array(historial),
            "posiciones_finales": posiciones.tolist(),
            "velocidades_finales": velocidades.tolist()
        }