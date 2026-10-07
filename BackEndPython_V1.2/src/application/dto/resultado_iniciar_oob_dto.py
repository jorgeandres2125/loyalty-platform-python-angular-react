from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoIniciarOobDTO:
    """AP-0005: resultado de iniciar un desafio de confirmacion OOB.

    `requiere_oob` False = la operacion no es critica y no exige confirmacion.
    `requiere_oob` True con `enviado` False = era critica pero no hay canal OOB
    disponible (fail-secure: la operacion no debe liberarse).
    """

    requiere_oob: bool
    enviado: bool = False
    desafio_id: str | None = None
    estado: str | None = None
    canal: str | None = None
    email_enmascarado: str | None = None
    expira_en_segundos: int | None = None
