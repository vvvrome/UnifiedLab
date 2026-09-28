from dataclasses import dataclass, field

from .validation import (
    validar_numero,
    validar_composicion
)


@dataclass
class Planet:
    nombre: str
    tipo: str

    masa: float
    radio: float
    distancia: float

    excentricidad: float = 0.0
    inclinacion: float = 0.0
    angulo_fase: float = 0.0

    albedo: float = 0.3
    gravedad: float = 0.0
    temperatura: float = 0.0

    rotacion: float = 24.0
    revolucion: float = 365.25

    anillos: int = 0
    lunas: int = 0

    magnetosfera: float = 0.0
    actividad: float = 0.0
    edad: float = 0.0
    metallicidad: float = 0.0

    presion: float = 0.0
    humedad: float = 0.0
    radiacion: float = 0.0
    actividad_solar: float = 0.0
    campo_magnetico: float = 0.0

    actividad_volcanica: float = 0.0
    actividad_tectonica: float = 0.0
    actividad_climatica: float = 0.0

    composicion: dict = field(default_factory=dict)
    atmosfera: dict = field(default_factory=dict)
    composicion_interior: dict = field(default_factory=dict)
    abundancia: dict = field(default_factory=dict)

    def __post_init__(self):
        self.nombre = self.nombre.strip()

        if not self.nombre:
            raise ValueError("El planeta necesita un nombre.")

        self.masa = validar_numero(
            self.masa, "Masa planetaria", minimo=0.000001
        )

        self.radio = validar_numero(
            self.radio, "Radio planetario", minimo=0.000001
        )

        self.distancia = validar_numero(
            self.distancia, "Distancia orbital", minimo=0.000001
        )

        self.excentricidad = validar_numero(
            self.excentricidad,
            "Excentricidad",
            minimo=0,
            maximo=0.999999
        )

        self.inclinacion = validar_numero(
            self.inclinacion,
            "Inclinación",
            minimo=0,
            maximo=180
        )

        self.angulo_fase = validar_numero(
            self.angulo_fase, "Ángulo orbital"
        )

        self.albedo = validar_numero(
            self.albedo, "Albedo", minimo=0, maximo=1
        )

    @classmethod
    def desde_formulario(cls, form):
        """Construye un planeta a partir de los campos HTML."""

        composicion = validar_composicion(
            form.get("composicion", "")
        )

        atmosfera = validar_composicion(
            form.get("Atmosfera", form.get("atmosfera", ""))
        )

        interior = validar_composicion(
            form.get(
                "ComposicionInterior",
                form.get("composicion_interior", "")
            )
        )

        abundancia = validar_composicion(
            form.get("Abundancia", form.get("abundancia", ""))
        )

        return cls(
            nombre=form.get("nombre", ""),
            tipo=form.get("tipo", "personalizado"),

            masa=form.get("masa"),
            radio=form.get("radio"),
            distancia=form.get("distancia"),

            excentricidad=form.get("Excentricidad", 0),
            inclinacion=form.get("Inclinacion", 0),

            angulo_fase=form.get(
                "Angulo_fase",
                form.get("angulo_fase", form.get("Angulo o fase", 0))
            ),

            albedo=form.get("Albedo", 0.3),
            gravedad=form.get("Gravedad", 0),
            temperatura=form.get("Temperatura", 0),

            rotacion=form.get("Rotacion", 24),
            revolucion=form.get("Revolucion", 365.25),

            anillos=int(float(form.get("Anillos", 0))),
            lunas=int(float(form.get("Lunas", 0))),

            magnetosfera=form.get("Magnetosfera", 0),
            actividad=form.get("Actividad", 0),
            edad=form.get("Edad", 0),
            metallicidad=form.get("Metallicidad", 0),

            presion=form.get("Presion", 0),
            humedad=form.get("Humedad", 0),
            radiacion=form.get("Radiacion", 0),
            actividad_solar=form.get("ActividadSolar", 0),
            campo_magnetico=form.get("CampoMagnetico", 0),

            actividad_volcanica=form.get("ActividadVolcanica", 0),
            actividad_tectonica=form.get("ActividadTectonica", 0),
            actividad_climatica=form.get("ActividadClimatica", 0),

            composicion=composicion,
            atmosfera=atmosfera,
            composicion_interior=interior,
            abundancia=abundancia
        )

    def to_dict(self):
        """Devuelve los datos del planeta como diccionario."""

        return {
            "nombre": self.nombre,
            "tipo": self.tipo,
            "masa": self.masa,
            "radio": self.radio,
            "distancia": self.distancia,
            "excentricidad": self.excentricidad,
            "inclinacion": self.inclinacion,
            "angulo_fase": self.angulo_fase,
            "albedo": self.albedo,
            "gravedad": self.gravedad,
            "temperatura": self.temperatura,
            "rotacion": self.rotacion,
            "revolucion": self.revolucion,
            "anillos": self.anillos,
            "lunas": self.lunas,
            "magnetosfera": self.magnetosfera,
            "actividad": self.actividad,
            "edad": self.edad,
            "metallicidad": self.metallicidad,
            "presion": self.presion,
            "humedad": self.humedad,
            "radiacion": self.radiacion,
            "actividad_solar": self.actividad_solar,
            "campo_magnetico": self.campo_magnetico,
            "actividad_volcanica": self.actividad_volcanica,
            "actividad_tectonica": self.actividad_tectonica,
            "actividad_climatica": self.actividad_climatica,
            "composicion": self.composicion,
            "atmosfera": self.atmosfera,
            "composicion_interior": self.composicion_interior,
            "abundancia": self.abundancia
        }