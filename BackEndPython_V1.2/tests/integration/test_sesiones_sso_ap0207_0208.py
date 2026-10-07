"""AP-0207 y AP-0208: gestion de sesiones SSO (listar/cerrar) y cierre global ante
cambio de contrasena.

AP-0207 (listar y cerrar sesiones) ya estaba implementado por AP-0130; su cobertura vive
en test_sesiones_router_ap0130.py. Aqui se blindan los dos huecos reales de AP-0208:

CR-1: el cambio de credencial subia token_version (invalidando los JWT) pero NO cerraba
      las sesiones en el Session Registry -> la lista de AP-0207 mostraba sesiones muertas
      como activas y no quedaba evidencia por sesion. Se cubre con un invariante que
      recorre TODOS los caminos de cambio de credencial.

CR-2: los tokens estandar OIDC retornaban antes de ValidadorSesion en require_token, asi
      que evadian token_version, la revocacion por sid y el estado del usuario (AP-0133).
      Un cambio de contrasena no los revocaba -> AP-0208 no se cumplia "en todas las
      aplicaciones".
"""
from __future__ import annotations

import inspect

from src.application.services.servicio_sesiones import ServicioSesiones
from src.application.use_cases.cambiar_password_expirada_use_case import (
    CambiarPasswordExpiradaUseCase,
)
from src.application.use_cases.cambiar_password_temporal_use_case import (
    CambiarPasswordTemporalUseCase,
)
from src.application.use_cases.emitir_password_temporal_use_case import (
    EmitirPasswordTemporalUseCase,
)
from src.application.use_cases.emitir_token_oidc_use_case import EmitirTokenOidcUseCase
from src.domain.services.politica_sesiones import PoliticaSesiones
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion
from src.infrastructure.external.in_memory_sesion_repo import InMemorySesionRepo

_CAMINOS_CAMBIO_CREDENCIAL = [
    CambiarPasswordExpiradaUseCase,
    CambiarPasswordTemporalUseCase,
    EmitirPasswordTemporalUseCase,
]


def _servicio_sesiones() -> ServicioSesiones:
    politica = PoliticaSesiones(max_canal=0, max_otras=0, roles_canal=frozenset())
    return ServicioSesiones(repo=InMemorySesionRepo(), politica=politica, habilitado=True)


async def _registrar(servicio: ServicioSesiones, sid: str, uid: int) -> None:
    await servicio.registrar(
        sid=sid, uid=uid, roles=[], jti="jti-" + sid, device_fp="fp",
        ip="127.0.0.1", user_agent="pytest",
    )


class TestInvarianteCierreGlobal:
    """AP-0208 / CR-1: todo camino que cambia la credencial debe poder cerrar sesiones."""

    def test_todos_los_caminos_aceptan_el_session_registry(self) -> None:
        # Si alguien anade un camino de cambio de credencial sin inyectar el registro,
        # subira token_version sin cerrar sesiones y AP-0207 volvera a mostrar sesiones
        # muertas. Este invariante lo detecta antes de produccion.
        for caso_de_uso in _CAMINOS_CAMBIO_CREDENCIAL:
            firma = inspect.signature(caso_de_uso.__init__)
            assert "sesiones" in firma.parameters, caso_de_uso.__name__

    def test_el_motivo_cambio_credencial_existe_en_el_catalogo(self) -> None:
        assert MotivoCierreSesion.CAMBIO_CREDENCIAL.value == "cambio_credencial"


class TestCierreGlobalDeSesiones:
    """AP-0208: cerrar_todas deja el registro coherente y con evidencia del motivo."""

    async def test_cerrar_todas_con_motivo_cambio_credencial(self) -> None:
        servicio = _servicio_sesiones()
        await _registrar(servicio, "s1", uid=1)
        await _registrar(servicio, "s2", uid=1)
        assert len(await servicio.listar(1)) == 2

        cerradas: int = await servicio.cerrar_todas(
            1, MotivoCierreSesion.CAMBIO_CREDENCIAL
        )

        assert cerradas == 2
        # AP-0207: tras el cambio de credencial la lista no muestra sesiones muertas.
        assert await servicio.listar(1) == []
        assert await servicio.esta_revocada("s1") is True
        assert await servicio.esta_revocada("s2") is True

    async def test_no_afecta_las_sesiones_de_otro_usuario(self) -> None:
        servicio = _servicio_sesiones()
        await _registrar(servicio, "s1", uid=1)
        await _registrar(servicio, "s9", uid=99)
        await servicio.cerrar_todas(1, MotivoCierreSesion.CAMBIO_CREDENCIAL)
        assert await servicio.esta_revocada("s9") is False
        assert len(await servicio.listar(99)) == 1


class TestTokenOidcPortaTokenVersion:
    """AP-0208 / CR-2: el token estandar SSO porta tv para poder ser revocado."""

    def test_emitir_acepta_token_version(self) -> None:
        firma = inspect.signature(EmitirTokenOidcUseCase.emitir)
        assert "token_version" in firma.parameters

    def test_el_claim_tv_viaja_en_el_token_estandar(self) -> None:
        capturado: dict[str, object] = {}

        class _ProveedorFake:
            def firmar(self, claims: dict[str, object]) -> str:
                capturado.update(claims)
                return "token-firmado"

            def clave_publica_pem(self) -> str:
                return ""

            def jwks(self) -> dict[str, object]:
                return {}

        uc = EmitirTokenOidcUseCase(
            proveedor=_ProveedorFake(),  # type: ignore[arg-type]
            issuer="https://sufi",
            audiencia="sufi",
            ttl_segundos=300,
            scope_default="openid",
        )
        uc.emitir(sub="551", roles=["comisionista"], token_version=7)
        # Sin este claim, un cambio de contrasena no podria invalidar el token SSO.
        assert capturado["tv"] == 7
