from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoDesafioOtpDTO:
    """AP-0012: resultado de emitir un desafio OTP de login (segundo factor)."""

    desafio_id: str
    email_enmascarado: str
    expira_en_segundos: int
