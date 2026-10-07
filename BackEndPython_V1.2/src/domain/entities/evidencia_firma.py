from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.algoritmo_firma import AlgoritmoFirma


@dataclass(frozen=True)
class EvidenciaFirma:
    """AP-0006: evidencia criptografica y verificable de una firma digital.

    Registro inmutable del acto de firmar un recurso sensible. Encadenado por hash
    (hash_anterior a hash_evidencia) para que el log de evidencias sea a prueba de
    manipulacion (tamper-evident): alterar una evidencia pasada rompe la cadena. No
    contiene la clave privada; referencia la clave publica por su kid.
    """

    id: str
    recurso_tipo: str
    recurso_id: str
    alg: AlgoritmoFirma
    kid: str
    hash_payload: str
    valor_firma: str
    emisor: str
    creado_en_iso: str
    hash_anterior: str
    hash_evidencia: str
