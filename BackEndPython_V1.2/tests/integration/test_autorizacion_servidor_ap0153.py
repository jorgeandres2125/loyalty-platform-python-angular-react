"""AP-0153: validaciones de autenticacion y autorizacion del lado del servidor.

El enforcement de permisos por endpoint (AP-0053), la autorizacion a nivel de objeto
(AP-0055) y la revalidacion de sesion (AP-0021/AP-0133) ya existen. Estas pruebas blindan
el requisito integral de AP-0153 ("Never Trust the Client"):

1. Fail-secure de configuracion: en staging y produccion la autorizacion del servidor no
   puede degradarse a auditoria ni apagarse.
2. Cobertura total: ningun endpoint autenticado puede quedar sin autorizacion del servidor
   (se reafirma el guard de AP-0053 con la lista de autoservicio como unica excepcion).
3. Semantica 401 (no autenticado) vs 403 (sin privilegios).
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from src.adapters.api.main import app as app_real
from src.domain.value_objects.permiso import Permiso
from src.infrastructure.config.dependencies import require_token
from src.infrastructure.config.permission_dependencies import require_permission
from src.infrastructure.config.settings import Settings

_AUTHZ_MODULE = "src.infrastructure.config.permission_dependencies"


def _prod_kwargs(**ov: object) -> dict[str, object]:
    base: dict[str, object] = {
        "jwt_secret_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
        "db_password": "xxxxxxxxxxxxxxxxxxxxxxxx",
        "db_user": "app_sufi",
        "smtp_password": "",
        "email_api_password": "",
        "kms_provider": "aws",
        "kms_key_id": "kms-test-key-id",
    }
    base.update(ov)
    return base


class TestFailSecureConfiguracion:
    """AP-0153: la autorizacion del servidor no puede debilitarse en un entorno real."""

    @pytest.mark.parametrize("entorno", ["staging", "production"])
    @pytest.mark.parametrize("modo", ["audit", "off"])
    def test_entorno_real_rechaza_authz_no_enforce(self, entorno: str, modo: str) -> None:
        with pytest.raises(ValueError, match="AUTHZ_ENFORCEMENT_MODE"):
            Settings(
                app_env=entorno,  # type: ignore[arg-type]
                authz_enforcement_mode=modo,
                **_prod_kwargs(),
            )

    @pytest.mark.parametrize("entorno", ["staging", "production"])
    @pytest.mark.parametrize("modo", ["audit", "off"])
    def test_entorno_real_rechaza_object_authz_no_enforce(
        self, entorno: str, modo: str
    ) -> None:
        with pytest.raises(ValueError, match="OBJECT_AUTHZ_MODE"):
            Settings(
                app_env=entorno,  # type: ignore[arg-type]
                object_authz_mode=modo,
                **_prod_kwargs(),
            )

    def test_produccion_por_defecto_es_enforce(self) -> None:
        s = Settings(app_env="production", **_prod_kwargs())  # type: ignore[arg-type]
        assert s.authz_enforcement_mode == "enforce"
        assert s.object_authz_mode == "enforce"

    def test_desarrollo_permite_modo_auditoria(self) -> None:
        s = Settings(app_env="development", authz_enforcement_mode="audit")
        assert s.authz_enforcement_mode == "audit"


class TestCoberturaServidor:
    """AP-0153: todo endpoint autenticado se autoriza en el servidor."""

    @staticmethod
    def _flatten(dependant: Any) -> Iterator[Any]:
        for dep in dependant.dependencies:
            yield dep
            yield from TestCoberturaServidor._flatten(dep)

    def _autentica(self, route: APIRoute) -> bool:
        return any(dep.call is require_token for dep in self._flatten(route.dependant))

    def _autoriza(self, route: APIRoute) -> bool:
        return any(
            getattr(dep.call, "__module__", "") == _AUTHZ_MODULE
            for dep in self._flatten(route.dependant)
        )

    def test_ningun_endpoint_autenticado_sin_autorizacion_de_servidor(self) -> None:
        # Reafirma el invariante de AP-0053 desde AP-0153: la unica excepcion admitida
        # es el autoservicio (el actor opera solo sobre si mismo, resuelto por el token).
        from tests.integration.test_rbac_cobertura import _AUTOSERVICIO

        faltantes: list[str] = sorted(
            route.path
            for route in app_real.routes
            if isinstance(route, APIRoute)
            and self._autentica(route)
            and not self._autoriza(route)
            and route.path not in _AUTOSERVICIO
        )
        assert not faltantes, f"AP-0153: endpoints sin autorizacion de servidor: {faltantes}"


class TestSemantica401Vs403:
    """AP-0153: 401 sin autenticacion, 403 con autenticacion pero sin permiso."""

    def _app(self) -> FastAPI:
        app = FastAPI()

        _guard = Depends(require_permission(Permiso.REPORTES_EXPORTAR))

        @app.get("/protegido", dependencies=[_guard])
        async def _protegido() -> dict[str, str]:
            return {"ok": "si"}

        return app

    def test_sin_token_responde_401(self) -> None:
        cliente = TestClient(self._app())
        resp = cliente.get("/protegido")
        assert resp.status_code == 401

    def test_autenticado_sin_permiso_responde_403(self) -> None:
        app = self._app()
        # Actor autenticado pero con un rol que NO tiene REPORTES_EXPORTAR.
        app.dependency_overrides[require_token] = lambda: {
            "sub": "1",
            "roles": ["comisionista"],
        }
        resp = TestClient(app).get("/protegido")
        assert resp.status_code == 403
