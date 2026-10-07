from __future__ import annotations


class PoliticaSesiones:
    """AP-0130 (Opcion D): maximo de sesiones concurrentes por tipo de aplicacion. El
    tipo se determina por los roles (canal vs otras). Un maximo de 0 significa ILIMITADO
    (modo 'solo informar', Opcion A): se registran y listan, pero no se expulsa."""

    def __init__(
        self, max_canal: int, max_otras: int, roles_canal: frozenset[str]
    ) -> None:
        self._max_canal: int = max_canal
        self._max_otras: int = max_otras
        self._roles_canal: frozenset[str] = roles_canal

    def es_canal(self, roles: list[str]) -> bool:
        return any(rol in self._roles_canal for rol in roles)

    def max_sesiones(self, roles: list[str]) -> int:
        return self._max_canal if self.es_canal(roles) else self._max_otras
