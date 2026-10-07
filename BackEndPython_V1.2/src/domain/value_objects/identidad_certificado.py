from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IdentidadCertificado:
    """AP-0003: identidad X.509 del certificado de cliente validado en el edge.

    Representa lo que el edge (Ingress o API Gateway) verifico durante el
    handshake mTLS y propago a la aplicacion: la huella (fingerprint SHA-256), el
    Subject (DN) y el numero de serie del certificado de cliente. Es material
    publico del certificado, nunca la clave privada. El fingerprint se normaliza
    (minusculas, sin dos puntos) para comparaciones estables contra la allow-list.
    """

    fingerprint: str
    subject: str
    serial: str

    def __post_init__(self) -> None:
        normalizada: str = self.fingerprint.replace(":", "").strip().lower()
        if not normalizada:
            raise ValueError("IdentidadCertificado requiere un fingerprint no vacio")
        object.__setattr__(self, "fingerprint", normalizada)
        object.__setattr__(self, "subject", self.subject.strip())
        object.__setattr__(self, "serial", self.serial.strip())
