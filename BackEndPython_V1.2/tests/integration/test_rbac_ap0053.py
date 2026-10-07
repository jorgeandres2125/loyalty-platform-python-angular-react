from __future__ import annotations

import asyncio

import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.domain.value_objects.permiso import Permiso
from src.infrastructure.config.dependencies import get_settings, require_token
from src.infrastructure.config.permission_dependencies import (
    require_admin_catalogos,
    require_admin_usuarios,
    require_permission,
)
from src.infrastructure.config.settings import Settings

SL = chr(47)


def _settings(modo: str) -> Settings:
    return Settings(authz_enforcement_mode=modo)  # type: ignore[call-arg]


def _tok(roles: list[str]) -> dict[str, object]:
    return {"sub": "5", "roles": roles}


class TestMotorRequirePermission:
    def test_enforce_deniega_rol_insuficiente(self) -> None:
        dep = require_permission(Permiso.REPORTES_EXPORTAR)
        with pytest.raises(HTTPException) as exc:
            asyncio.run(dep(_tok(["comisionista"]), _settings("enforce")))
        assert exc.value.status_code == 403

    def test_enforce_autoriza_rol_con_permiso(self) -> None:
        dep = require_permission(Permiso.REPORTES_EXPORTAR)
        salida = asyncio.run(dep(_tok(["asesor_comercial"]), _settings("enforce")))
        assert salida["sub"] == "5"

    def test_administrator_es_superusuario(self) -> None:
        dep = require_permission(Permiso.INACTIVACION_AUTORIZAR)
        assert asyncio.run(dep(_tok(["administrator"]), _settings("enforce")))["sub"] == "5"

    def test_audit_registra_pero_deja_pasar(self) -> None:
        dep = require_permission(Permiso.REPORTES_EXPORTAR)
        assert asyncio.run(dep(_tok(["comisionista"]), _settings("audit")))["sub"] == "5"

    def test_any_basta_uno_de_los_permisos(self) -> None:
        dep = require_permission(
            Permiso.MOVILIDAD_PERFIL_VER_PROPIO, Permiso.CONSUMO_PERFIL_VER_PROPIO
        )
        assert asyncio.run(dep(_tok(["comisionista_consumo"]), _settings("enforce")))["sub"] == "5"


class TestGuardiasAdministracion:
    def test_catalogos_solo_administrator(self) -> None:
        with pytest.raises(HTTPException) as exc:
            require_admin_catalogos(_tok(["webmaster"]))
        assert exc.value.status_code == 403
        assert require_admin_catalogos(_tok(["administrator"]))["sub"] == "5"

    def test_usuarios_administrator_o_webmaster(self) -> None:
        assert require_admin_usuarios(_tok(["webmaster"]))["sub"] == "5"
        with pytest.raises(HTTPException):
            require_admin_usuarios(_tok(["comisionista"]))


class TestEscalamientoVerticalHttp:
    def _cliente(self, modo: str, roles: list[str]) -> TestClient:
        mini = FastAPI()

        @mini.get(
            SL + "staff",
            dependencies=[Depends(require_permission(Permiso.MOVILIDAD_ASESORES_GESTIONAR))],
        )
        def staff() -> dict[str, bool]:
            return {"ok": True}

        mini.dependency_overrides[require_token] = lambda: {"sub": "9", "roles": roles}
        mini.dependency_overrides[get_settings] = lambda: _settings(modo)
        return TestClient(mini, raise_server_exceptions=False)

    def test_comisionista_no_accede_a_funcion_de_staff(self) -> None:
        assert self._cliente("enforce", ["comisionista"]).get(SL + "staff").status_code == 403

    def test_asesor_si_accede(self) -> None:
        assert self._cliente("enforce", ["asesor_comercial"]).get(SL + "staff").status_code == 200

    def test_audit_no_bloquea(self) -> None:
        assert self._cliente("audit", ["comisionista"]).get(SL + "staff").status_code == 200
