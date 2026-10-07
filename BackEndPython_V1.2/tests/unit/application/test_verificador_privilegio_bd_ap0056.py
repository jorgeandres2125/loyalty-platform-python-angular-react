from __future__ import annotations

import asyncio
import logging

import pytest

from src.application.services.verificador_privilegio_bd import VerificadorPrivilegioBd
from src.domain.exceptions.privilegio_bd_excesivo import PrivilegioBdExcesivo
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD


class _FakeSonda:
    def __init__(
        self, roles: list[str] | None = None, exc: Exception | None = None
    ) -> None:
        self._roles: list[str] = list(roles or [])
        self._exc: Exception | None = exc
        self.llamado: bool = False

    async def roles_privilegiados(self) -> list[str]:
        self.llamado = True
        if self._exc is not None:
            raise self._exc
        return list(self._roles)


class _CaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _verif(
    roles: list[str] | None = None,
    exc: Exception | None = None,
    app_env: str = "production",
    habilitado: bool = True,
) -> tuple[VerificadorPrivilegioBd, _FakeSonda]:
    sonda = _FakeSonda(roles, exc)
    verif = VerificadorPrivilegioBd(sonda, app_env, habilitado)  # type: ignore[arg-type]
    return verif, sonda


def test_sin_roles_privilegiados_pasa() -> None:
    verif, sonda = _verif(roles=[], app_env="production")
    asyncio.run(verif.verificar())  # no debe lanzar
    assert sonda.llamado is True


def test_privilegiado_en_produccion_fail_fast() -> None:
    verif, _ = _verif(roles=["sysadmin"], app_env="production")
    with pytest.raises(PrivilegioBdExcesivo):
        asyncio.run(verif.verificar())


def test_privilegiado_en_staging_fail_fast() -> None:
    verif, _ = _verif(roles=["db_owner"], app_env="staging")
    with pytest.raises(PrivilegioBdExcesivo):
        asyncio.run(verif.verificar())


def test_privilegiado_en_dev_solo_warning() -> None:
    verif, _ = _verif(roles=["db_ddladmin"], app_env="development")
    logger = logging.getLogger(LOGGER_SEGURIDAD)
    handler = _CaptureHandler()
    logger.addHandler(handler)
    try:
        asyncio.run(verif.verificar())  # no debe lanzar en dev
    finally:
        logger.removeHandler(handler)
    assert any(
        r.levelno == logging.WARNING and "db_ddladmin" in r.getMessage()
        for r in handler.records
    )


def test_sondeo_falla_no_rompe_arranque() -> None:
    verif, _ = _verif(exc=RuntimeError("conexion caida"), app_env="production")
    asyncio.run(verif.verificar())  # best-effort: no debe lanzar


def test_deshabilitado_no_sondea() -> None:
    verif, sonda = _verif(roles=["sysadmin"], app_env="production", habilitado=False)
    asyncio.run(verif.verificar())  # no lanza aunque el fake sea privilegiado
    assert sonda.llamado is False
