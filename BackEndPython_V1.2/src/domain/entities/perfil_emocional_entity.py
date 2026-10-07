from dataclasses import dataclass


@dataclass
class PerfilEmocionalEntity:
    numero_documento: str
    con_quien_vives: str | None = None
    estado_civil: str | None = None
    numero_hijos: str | None = None
    info_hijos: str | None = None
    hobbies: str | None = None
    premios_gustaria_recibir: str | None = None
    nivel_educativo: str | None = None
    profesion: str | None = None
    numero_mascotas: str | None = None
    info_mascotas: str | None = None
    temas_a_profundizar: str | None = None
    acepto_terminos_y_condiciones: int | None = None
    comisionista_programa_id: int | None = None
    info_premios: str | None = None
    propositos_familiares: str | None = None
    propositos_financieros: str | None = None
    propositos_diversion: str | None = None
    propositos_salud: str | None = None
    propositos_competencias: str | None = None
