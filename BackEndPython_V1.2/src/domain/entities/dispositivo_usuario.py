from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class DispositivoUsuario:
    """AP-0014: dispositivo (equipo origen) desde el que un usuario se autentica.

    Inmutable, indexado por (uid, device_hash). device_hash es la huella normalizada del
    equipo (del fingerprint del navegador o, en su defecto, del User-Agent). Registra el
    primer y ultimo acceso, cuantas veces se ha visto y si el usuario lo marco como de
    confianza. Permite reconocer equipos ya autorizados y detectar accesos desde equipos
    desconocidos.
    """

    uid: int
    device_hash: str
    device_name: str
    user_agent: str
    first_login_iso: str
    last_login_iso: str
    veces_visto: int
    trusted: bool

    def con_acceso(self, cuando_iso: str) -> DispositivoUsuario:
        return replace(
            self, last_login_iso=cuando_iso, veces_visto=self.veces_visto + 1
        )
