from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoSolicitudCodigoDTO:
    """Resultado de solicitar un código de verificación (AP-0004).

    Anti-enumeración: ante un documento inexistente o sin correo, `enviado=False`
    y `email_enmascarado=None`; la capa HTTP responde igual (202) en todos los casos.
    """

    enviado: bool
    email_enmascarado: str | None = None
    expira_en_horas: int | None = None
    en_cooldown: bool = False
