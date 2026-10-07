from enum import Enum


class RolUsuario(str, Enum):
    ANONIMO = "anonimo"
    AUTENTICADO = "autenticado"
    ADMINISTRATOR = "administrator"
    COMISIONISTA = "comisionista"
    COMISIONISTA_CONSUMO = "comisionista_consumo"
    WEBMASTER = "webmaster"
    ASESOR_LOGISTICO = "asesor_logistico"
    ASESOR_COMERCIAL = "asesor_comercial"
    ASESOR_CALLCENTER = "asesor_callcenter"
    DOCUMENTADOR = "documentador"
    ASESOR_CONSUMO = "asesor_consumo"
    EJECUTIVO_CONSUMO = "ejecutivo_consumo"
    TELEPERFORMANCE = "teleperformance"
    EJECUTIVO_MOVILIDAD_CONSUMO = "ejecutivo_movilidad_consumo"

    @classmethod
    def desde_legacy(cls, nombre_legacy: str) -> "RolUsuario":
        """Convierte el nombre con espacios del snapshot Drupal al slug canónico."""
        mapa = {
            "usuario anónimo": cls.ANONIMO,
            "usuario autenticado": cls.AUTENTICADO,
            "administrator": cls.ADMINISTRATOR,
            "comisionista": cls.COMISIONISTA,
            "comisionista consumo": cls.COMISIONISTA_CONSUMO,
            "webmaster": cls.WEBMASTER,
            "asesor logistico": cls.ASESOR_LOGISTICO,
            "asesor comercial": cls.ASESOR_COMERCIAL,
            "asesor callcenter": cls.ASESOR_CALLCENTER,
            "documentador": cls.DOCUMENTADOR,
            "asesor consumo": cls.ASESOR_CONSUMO,
            "ejecutivo consumo": cls.EJECUTIVO_CONSUMO,
            "teleperformance": cls.TELEPERFORMANCE,
            "ejecutivo movilidad-consumo": cls.EJECUTIVO_MOVILIDAD_CONSUMO,
        }
        try:
            return mapa[nombre_legacy.lower()]
        except KeyError:
            raise ValueError(f"Rol desconocido: '{nombre_legacy}'")
