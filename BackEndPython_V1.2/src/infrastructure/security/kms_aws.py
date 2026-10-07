from __future__ import annotations

from typing import Any

from src.domain.exceptions.cifrado_error import CifradoError


class KmsAws:
    """Adaptador del KMS de AWS para produccion (AP-0180).

    El KEK (CMK) reside en AWS KMS y NUNCA entra al proceso: envolver o desenvolver
    la DEK se delega al servicio con las APIs Encrypt y Decrypt. respaldado_por_hsm
    es True (las CMK de KMS pueden respaldarse en HSM FIPS 140-2). Requiere boto3 y
    credenciales de AWS inyectadas en el entorno de despliegue. Satisface por
    estructura el puerto GestorClaveMaestra (PEP 544).
    """

    def __init__(self, key_id: str) -> None:
        if not key_id:
            raise CifradoError("kms_key_id requerido para el proveedor AWS KMS")
        try:
            import boto3
        except ImportError as exc:
            raise CifradoError(
                "boto3 no esta instalado; requerido por el proveedor AWS KMS (AP-0180)"
            ) from exc
        self._key_id: str = key_id
        self._cliente: Any = boto3.client("kms")

    @property
    def respaldado_por_hsm(self) -> bool:
        return True

    def cifrar_clave_datos(self, clave_datos: bytes) -> bytes:
        respuesta: dict[str, Any] = self._cliente.encrypt(
            KeyId=self._key_id, Plaintext=clave_datos
        )
        return bytes(respuesta["CiphertextBlob"])

    def descifrar_clave_datos(self, envoltura: bytes) -> bytes:
        respuesta: dict[str, Any] = self._cliente.decrypt(CiphertextBlob=envoltura)
        return bytes(respuesta["Plaintext"])
