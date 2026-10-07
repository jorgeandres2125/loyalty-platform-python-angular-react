from __future__ import annotations


class PoliticaInactividad:
    """AP-0129: limite de inactividad de sesion. Canales 7 min, otras aplicaciones 20 min.

    El tipo de aplicacion se determina por los roles del usuario: los roles de cara al
    cliente (comisionista, ejecutivo, asesores) son canales; el resto (back-office) son
    otras aplicaciones. Es un servicio de dominio sin estado ni dependencias de framework.
    """

    def __init__(
        self, minutos_canal: int, minutos_otras: int, roles_canal: frozenset[str]
    ) -> None:
        self._minutos_canal: int = minutos_canal
        self._minutos_otras: int = minutos_otras
        self._roles_canal: frozenset[str] = roles_canal

    def es_canal(self, roles: list[str]) -> bool:
        return any(rol in self._roles_canal for rol in roles)

    def limite_minutos(self, roles: list[str]) -> int:
        return self._minutos_canal if self.es_canal(roles) else self._minutos_otras
