from __future__ import annotations

import pytest

from src.domain.exceptions.cifrado_error import CifradoError
from src.infrastructure.security.kms_local_software import KmsLocalSoftware


def _kms() -> KmsLocalSoftware:
    return KmsLocalSoftware(bytes(32))


class TestKmsLocalSoftware:
    def test_round_trip(self) -> None:
        kms = _kms()
        dek = bytes(range(32))
        envoltura = kms.cifrar_clave_datos(dek)
        assert kms.descifrar_clave_datos(envoltura) == dek

    def test_envoltura_distinta_cada_vez(self) -> None:
        kms = _kms()
        dek = bytes(32)
        assert kms.cifrar_clave_datos(dek) != kms.cifrar_clave_datos(dek)

    def test_no_respaldado_por_hsm(self) -> None:
        assert _kms().respaldado_por_hsm is False

    def test_rechaza_kek_corta(self) -> None:
        with pytest.raises(CifradoError):
            KmsLocalSoftware(bytes(16))

    def test_rechaza_envoltura_corta(self) -> None:
        with pytest.raises(CifradoError):
            _kms().descifrar_clave_datos(bytes(8))
