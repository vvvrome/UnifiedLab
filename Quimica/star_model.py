from dataclasses import dataclass, field

from .validation import (
    validar_numero,
    validar_composicion
)


@dataclass
class Star:
    nombre: str
    tipo: str

    masa: float
    radio: float
    temperatura: float

    luminosidad: float
    edad: float
    metallicidad: float

    composicion: dict = field(default_factory=dict)
    abundancia: dict = field(default_factory=dict)

    def __post_init__(self):
        self.nombre = self.nombre.strip()

        if not self.nombre:
            raise ValueError("La estrella necesita un nombre.")

        self.masa = validar_numero(
            self.masa, "Masa estelar", minimo=0.000001
        )

        self.radio = validar_numero(
            self.radio, "Radio estelar", minimo=0.000001
        )

        self.temperatura = validar_numero(
            self.temperatura,
            "Temperatura",
            minimo=0.1
        )

        self.luminosidad = validar_numero(
            self.luminosidad,
            "Luminosidad",
            minimo=0
        )

        self.edad = validar_numero(
            self.edad, "Edad", minimo=0
        )

        self.metallicidad = validar_numero(
            self.metallicidad, "Metallicidad"
        )

    @classmethod
    def desde_formulario(cls, form):
        """Construye una estrella desde request.form de Flask."""

        composicion = validar_composicion(
            form.get("composicion", "")
        )

        abundancia_texto = form.get(
            "abundancia",
            form.get("Abundancia", "")
        )

        abundancia = validar_composicion(abundancia_texto)

        return cls(
            nombre=form.get("nombre", ""),
            tipo=form.get("tipo", "personalizada"),

            masa=form.get("masa"),
            radio=form.get("radio"),
            temperatura=form.get("temperatura"),

            luminosidad=form.get(
                "Luminosidad",
                form.get("luminosidad")
            ),

            edad=form.get("edad"),

            metallicidad=form.get(
                "metallicidad",
                form.get("Metallicidad", 0)
            ),

            composicion=composicion,
            abundancia=abundancia
        )

    def to_dict(self):
        """Convierte la estrella en un diccionario para Flask/Jinja."""

        return {
            "nombre": self.nombre,
            "tipo": self.tipo,
            "masa": self.masa,
            "radio": self.radio,
            "temperatura": self.temperatura,
            "luminosidad": self.luminosidad,
            "edad": self.edad,
            "metallicidad": self.metallicidad,
            "composicion": self.composicion,
            "abundancia": self.abundancia
        }