from __future__ import annotations

import asyncio
import logging

import pytest

from src.application.services.verificador_permisos_objeto import (
    VerificadorPermisosObjeto,
)
from src.domain.exceptions.permiso_objeto_excesivo import PermisoObjetoExcesivo
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD

_ANOMALIA: str = "EXECUTE a nivel de base de datos"


class _FakeSonda:
    def __init__(
        self, anomalias: list[str] | None = None, exc: Exception | None = None
    ) -> None:
        self._anomalias: list[str] = list(anomalias or [])
        self._exc: Exception | None = exc
        self.llamado: bool = False

    async def anomalias_minimo_privilegio(self) -> list[str]:
        self.llamado = True
        if self._exc is not None:
            raise self._exc
        return list(self._anomalias)


class _CaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _verif(
    anomalias: list[str] | None = None,
    exc: Exception | None = None,
    app_env: str = "production",
    habilitado: bool = True,
) -> tuple[VerificadorPermisosObjeto, _FakeSonda]:
    sonda = _FakeSonda(anomalias, exc)
    verif = VerificadorPermisosObjeto(sonda, app_env, habilitado)
    return verif, sonda


def test_sin_anomalias_pasa() -> None:
    verif, sonda = _verif(anomalias=[], app_env="production")
    asyncio.run(verif.verificar())
    assert sonda.llamado is True


def test_anomalia_en_produccion_fail_fast() -> None:
    verif, _ = _verif(anomalias=[_ANOMALIA], app_env="production")
    with pytest.raises(PermisoObjetoExcesivo):
        asyncio.run(verif.verificar())


def test_anomalia_en_staging_fail_fast() -> None:
    verif, _ = _verif(anomalias=[_ANOMALIA], app_env="staging")
    with pytest.raises(PermisoObjetoExcesivo):
        asyncio.run(verif.verificar())


def test_anomalia_en_dev_solo_warning() -> None:
    verif, _ = _verif(anomalias=[_ANOMALIA], app_env="development")
    logger = logging.getLogger(LOGGER_SEGURIDAD)
    handler = _CaptureHandler()
    logger.addHandler(handler)
    try:
        asyncio.run(verif.verificar())
    finally:
        logger.removeHandler(handler)
    assert any(
        r.levelno == logging.WARNING and _ANOMALIA in r.getMessage()
        for r in handler.records
    )


def test_sondeo_falla_no_rompe_arranque() -> None:
    verif, _ = _verif(exc=RuntimeError("conexion caida"), app_env="production")
    asyncio.run(verif.verificar())


def test_deshabilitado_no_sondea() -> None:
    verif, sonda = _verif(
        anomalias=[_ANOMALIA], app_env="production", habilitado=False
    )
    asyncio.run(verif.verificar())
    assert sonda.llamado is False
