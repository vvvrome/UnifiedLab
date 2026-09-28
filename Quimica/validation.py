import json
import math
import re
from pathlib import Path


ELEMENTS_PATH = Path(__file__).parent / "elements.json"


def cargar_elementos():
    """Carga el catálogo químico desde elements.json."""

    if not ELEMENTS_PATH.exists():
        raise FileNotFoundError(
            f"No se encuentra el archivo: {ELEMENTS_PATH}"
        )

    with open(ELEMENTS_PATH, "r", encoding="utf-8") as archivo:
        data = json.load(archivo)

    # Admite un JSON con lista de elementos o diccionario.
    if isinstance(data, list):
        return {
            elemento["symbol"]
            for elemento in data
            if isinstance(elemento, dict)
            and "symbol" in elemento
        }

    if isinstance(data, dict):
        if "elements" in data and isinstance(data["elements"], list):
            return {
                elemento["symbol"]
                for elemento in data["elements"]
                if isinstance(elemento, dict)
                and "symbol" in elemento
            }

        # Si las claves son símbolos químicos.
        return set(data.keys())

    raise ValueError("Formato no reconocido en elements.json")


def validar_numero(valor, nombre, minimo=None, maximo=None):
    """Convierte un valor a float y comprueba sus límites."""

    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} debe ser un número válido.")

    if not math.isfinite(numero):
        raise ValueError(f"{nombre} debe ser un número finito.")

    if minimo is not None and numero < minimo:
        raise ValueError(f"{nombre} debe ser >= {minimo}.")

    if maximo is not None and numero > maximo:
        raise ValueError(f"{nombre} debe ser <= {maximo}.")

    return numero


def validar_composicion(texto, exigir_100=True):
    """
    Recibe una composición como:
    H:70, He:28, O:1, Fe:1

    Devuelve un diccionario:
    {"H": 70.0, "He": 28.0, "O": 1.0, "Fe": 1.0}
    """

    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("La composición química está vacía.")

    elementos_validos = cargar_elementos()
    composicion = {}

    partes = texto.split(",")

    for parte in partes:
        parte = parte.strip()

        coincidencia = re.fullmatch(
            r"([A-Z][a-z]?):\s*(\d+(?:[.,]\d+)?)",
            parte
        )

        if not coincidencia:
            raise ValueError(
                f"Formato incorrecto: '{parte}'. "
                "Usa, por ejemplo, H:70, He:28, O:1, Fe:1"
            )

        simbolo = coincidencia.group(1)
        porcentaje = float(
            coincidencia.group(2).replace(",", ".")
        )

        if simbolo not in elementos_validos:
            raise ValueError(
                f"El elemento químico '{simbolo}' "
                "no aparece en elements.json."
            )

        if simbolo in composicion:
            raise ValueError(
                f"El elemento '{simbolo}' está repetido."
            )

        if porcentaje < 0:
            raise ValueError(
                f"El porcentaje de {simbolo} no puede ser negativo."
            )

        composicion[simbolo] = porcentaje

    if exigir_100:
        total = sum(composicion.values())

        if not math.isclose(total, 100.0, abs_tol=0.05):
            raise ValueError(
                f"La composición suma {total:.2f} %. "
                "Debe sumar 100 %."
            )

    return composicion


def validar_rango(valor, nombre, minimo, maximo):
    """Valida un valor dentro de un intervalo."""

    return validar_numero(
        valor,
        nombre,
        minimo=minimo,
        maximo=maximo
    )