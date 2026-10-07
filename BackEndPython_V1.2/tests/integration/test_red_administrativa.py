from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.types import ASGIApp

from src.adapters.api.main import app as app_real
from src.adapters.api.middleware.red_administrativa_middleware import (
    RedAdministrativaMiddleware,
)
from src.shared.constants.red_admin import (
    HEADER_RED_ADMIN_EDGE_SECRET,
    RUTAS_ADMIN_RED,
)

SL = chr(47)
_SECRET = "edge-secret"
_XFF = "X-Forwarded-For"
_CIDRS = ("10.0.0.0" + SL + "8",)
_ADMIN = RUTAS_ADMIN_RED[0] + SL + "ping"
_PUB = SL + "publico"


async def _asgi_noop(scope: object, receive: object, send: object) -> None:
    return None


def _mw(cidrs: tuple[str, ...]) -> RedAdministrativaMiddleware:
    app: ASGIApp = _asgi_noop  # type: ignore[assignment]
    return RedAdministrativaMiddleware(
        app,
        cidrs_gestion=cidrs,
        rutas_restringidas=RUTAS_ADMIN_RED,
        edge_secret=_SECRET,
        trusted_ip_header=_XFF,
        enabled=True,
    )


def _mini_app(enabled: bool) -> FastAPI:
    mini = FastAPI()
    mini.add_middleware(
        RedAdministrativaMiddleware,
        cidrs_gestion=_CIDRS,
        rutas_restringidas=RUTAS_ADMIN_RED,
        edge_secret=_SECRET,
        trusted_ip_header=_XFF,
        enabled=enabled,
    )

    @mini.get(_ADMIN)
    def protegido() -> dict[str, bool]:
        return {"ok": True}

    @mini.get(_PUB)
    def publico() -> dict[str, bool]:
        return {"ok": True}

    return mini


_ON = TestClient(_mini_app(True))
_OFF = TestClient(_mini_app(False))


class TestParseoYRango:
    def test_ignora_cidr_malformado(self) -> None:
        mw = _mw(("malo", "10.0.0.0" + SL + "8"))
        assert len(mw._redes) == 1

    def test_en_red_gestion(self) -> None:
        mw = _mw(_CIDRS)
        assert mw._en_red_gestion("10.5.5.5") is True
        assert mw._en_red_gestion("8.8.8.8") is False
        assert mw._en_red_gestion("no-es-ip") is False


class TestRedAdministrativaMiddleware:
    def test_admin_sin_origen_confiable_da_403(self) -> None:
        assert _ON.get(_ADMIN).status_code == 403

    def test_admin_ip_en_red_gestion_da_200(self) -> None:
        resp = _ON.get(
            _ADMIN,
            headers={_XFF: "10.1.2.3", HEADER_RED_ADMIN_EDGE_SECRET: _SECRET},
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_ip_reenviada_sin_secreto_se_ignora_403(self) -> None:
        resp = _ON.get(_ADMIN, headers={_XFF: "10.1.2.3"})
        assert resp.status_code == 403

    def test_secreto_invalido_ignora_xff_403(self) -> None:
        resp = _ON.get(
            _ADMIN,
            headers={_XFF: "10.1.2.3", HEADER_RED_ADMIN_EDGE_SECRET: "malo"},
        )
        assert resp.status_code == 403

    def test_ip_fuera_de_red_gestion_da_403(self) -> None:
        resp = _ON.get(
            _ADMIN,
            headers={_XFF: "8.8.8.8", HEADER_RED_ADMIN_EDGE_SECRET: _SECRET},
        )
        assert resp.status_code == 403

    def test_ruta_no_admin_no_se_restringe(self) -> None:
        assert _ON.get(_PUB).status_code == 200

    def test_deshabilitado_no_bloquea(self) -> None:
        assert _OFF.get(_ADMIN).status_code == 200


def test_app_real_registra_red_admin_middleware() -> None:
    clases: list[str] = [
        getattr(m.cls, "__name__", "") for m in app_real.user_middleware
    ]
    assert RedAdministrativaMiddleware.__name__ in clases


class TestValidadorProduccion:
    @staticmethod
    def _prod_kwargs() -> dict[str, object]:
        return {
            "jwt_secret_key": "x" * 24,
            "db_password": "x" * 24,
            "db_user": "app_sufi",
            "smtp_password": "",
            "email_api_password": "",
            "kms_provider": "aws",
            "kms_key_id": "kms-test-key-id",
        }

    def test_produccion_sin_cidrs_falla(self) -> None:
        import pytest
        from pydantic import ValidationError

        from src.infrastructure.config.settings import Settings

        with pytest.raises(ValidationError):
            Settings(  # type: ignore[arg-type]
                app_env="production", red_admin_cidrs="", **self._prod_kwargs()
            )

    def test_produccion_con_cidrs_habilita(self) -> None:
        from src.infrastructure.config.settings import Settings

        s = Settings(  # type: ignore[arg-type]
            app_env="production",
            red_admin_cidrs="10.0.0.0" + SL + "8",
            red_admin_edge_secret="secreto-edge",
            **self._prod_kwargs(),
        )
        assert s.red_admin_enabled is True
