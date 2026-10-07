from __future__ import annotations


class TokenSapinInvalido(Exception):
    """AP-0075: el token SAPIN v2 (AES-256-GCM) no pudo autenticarse ni descifrarse (tag
    invalido, formato incorrecto o clave GCM no configurada)."""
