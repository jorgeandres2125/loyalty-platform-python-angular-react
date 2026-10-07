from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrincipalCertificado:
    """AP-0003: principal de negocio resuelto a partir del certificado de cliente.

    Es el resultado de mapear una IdentidadCertificado (huella X.509) a la
    identidad logica del sistema que consume el API: el sistema o integracion
    (por ejemplo "ingesta-mainframe" o "sapin"), la empresa a la que pertenece y
    si la asignacion esta activa. Un principal inactivo se trata como no
    autenticado (defensa en profundidad frente a la revocacion en la PKI).
    """

    sistema: str
    empresa: str
    activo: bool = True

    def __post_init__(self) -> None:
        if not self.sistema.strip():
            raise ValueError("PrincipalCertificado requiere 'sistema' no vacio")
        object.__setattr__(self, "sistema", self.sistema.strip())
        object.__setattr__(self, "empresa", self.empresa.strip())
