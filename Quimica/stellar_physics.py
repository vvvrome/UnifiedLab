import math


# Constantes físicas
G = 6.67430e-11

MASA_SOL = 1.98847e30
RADIO_SOL = 6.957e8
LUMINOSIDAD_SOL = 3.828e26

SIGMA = 5.670374419e-8


def calcular_densidad(masa_kg, radio_m):
    """Densidad media en kg/m³."""

    volumen = (4 / 3) * math.pi * radio_m**3
    return masa_kg / volumen


def calcular_gravedad_superficial(masa_kg, radio_m):
    """Gravedad superficial en m/s²."""

    return G * masa_kg / radio_m**2


def calcular_velocidad_escape(masa_kg, radio_m):
    """Velocidad de escape en m/s."""

    return math.sqrt(2 * G * masa_kg / radio_m)


def calcular_luminosidad_teorica(radio_m, temperatura_k):
    """Luminosidad aproximada mediante Stefan-Boltzmann."""

    return (
        4
        * math.pi
        * radio_m**2
        * SIGMA
        * temperatura_k**4
    )


def calcular_radio_solar(radio_solar):
    return radio_solar * RADIO_SOL


def calcular_masa_solar(masa_solar):
    return masa_solar * MASA_SOL


def analizar_estrella(estrella):
    """
    Recibe un objeto Star.
    Devuelve sus propiedades físicas calculadas.
    """

    masa_kg = calcular_masa_solar(estrella.masa)
    radio_m = calcular_radio_solar(estrella.radio)

    luminosidad_w = (
        estrella.luminosidad * LUMINOSIDAD_SOL
    )

    luminosidad_teorica = calcular_luminosidad_teorica(
        radio_m,
        estrella.temperatura
    )

    return {
        "masa_kg": masa_kg,
        "radio_m": radio_m,

        "densidad_kg_m3": calcular_densidad(
            masa_kg, radio_m
        ),

        "gravedad_m_s2": calcular_gravedad_superficial(
            masa_kg, radio_m
        ),

        "velocidad_escape_m_s": calcular_velocidad_escape(
            masa_kg, radio_m
        ),

        "luminosidad_w": luminosidad_w,

        "luminosidad_teorica_w": luminosidad_teorica,

        "luminosidad_solar_teorica":
            luminosidad_teorica / LUMINOSIDAD_SOL
    }