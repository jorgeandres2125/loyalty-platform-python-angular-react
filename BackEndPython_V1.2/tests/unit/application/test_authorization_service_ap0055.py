from __future__ import annotations

import asyncio

from src.application.services.authorization_service import AuthorizationService
from src.application.services.permission_evaluator import PermissionEvaluator
from src.domain.value_objects.accion_recurso import AccionRecurso
from src.domain.value_objects.resource_type import ResourceType
from src.domain.value_objects.rol_usuario import RolUsuario


class _FakeOwnership:
    def __init__(self, es_dueno: bool) -> None:
        self._es_dueno: bool = es_dueno
        self.consultado: bool = False

    async def es_propietario(
        self, actor_uid: int, tipo: ResourceType, resource_id: str
    ) -> bool:
        self.consultado = True
        return self._es_dueno


class _FakeAuditor:
    def __init__(self) -> None:
        self.registros: list[tuple[bool, str, str]] = []

    async def registrar(
        self,
        actor_uid: int,
        tipo: ResourceType,
        resource_id: str | None,
        accion: AccionRecurso,
        permitido: bool,
        motivo: str,
        modo: str,
    ) -> None:
        self.registros.append((permitido, motivo, modo))


def _svc(
    es_dueno: bool = True, modo: str = "enforce"
) -> tuple[AuthorizationService, _FakeOwnership, _FakeAuditor]:
    own = _FakeOwnership(es_dueno)
    aud = _FakeAuditor()
    svc = AuthorizationService(
        permission_evaluator=PermissionEvaluator(),
        ownership_validator=own,  # type: ignore[arg-type]
        auditor=aud,  # type: ignore[arg-type]
        modo=modo,
    )
    return svc, own, aud


_COMISIONISTA = frozenset({RolUsuario.COMISIONISTA})
_CONSUMO = frozenset({RolUsuario.COMISIONISTA_CONSUMO})
_STAFF = frozenset({RolUsuario.ASESOR_COMERCIAL})


class TestDocumento:
    def test_dueno_permitido(self) -> None:
        svc, _own, aud = _svc(es_dueno=True)
        d = asyncio.run(
            svc.autorizar(7, _COMISIONISTA, ResourceType.DOCUMENTO, AccionRecurso.CREATE, "123")
        )
        assert d.permitido is True
        assert aud.registros[-1][0] is True

    def test_no_dueno_denegado_403(self) -> None:
        svc, _own, aud = _svc(es_dueno=False)
        d = asyncio.run(
            svc.autorizar(7, _COMISIONISTA, ResourceType.DOCUMENTO, AccionRecurso.CREATE, "999")
        )
        assert d.permitido is False
        assert d.status == 403
        assert aud.registros[-1] == (False, "ownership", "enforce")

    def test_staff_omite_ownership(self) -> None:
        svc, own, _aud = _svc(es_dueno=False)
        d = asyncio.run(
            svc.autorizar(50, _STAFF, ResourceType.DOCUMENTO, AccionRecurso.CREATE, "999")
        )
        assert d.permitido is True
        assert own.consultado is False


class TestTokenSapin:
    def test_dueno_permitido(self) -> None:
        svc, _own, _aud = _svc(es_dueno=True)
        d = asyncio.run(
            svc.autorizar(7, _CONSUMO, ResourceType.TOKEN_SAPIN, AccionRecurso.CREATE, "123")
        )
        assert d.permitido is True

    def test_cedula_ajena_denegada_sin_bypass(self) -> None:
        # staff no tiene bypass en SAPIN: si no es dueno, se deniega igual.
        svc, _own, _aud = _svc(es_dueno=False)
        d = asyncio.run(
            svc.autorizar(50, _STAFF, ResourceType.TOKEN_SAPIN, AccionRecurso.CREATE, "999")
        )
        assert d.permitido is False
        assert d.status == 403


class TestDesafioOob:
    def test_titular_permitido(self) -> None:
        svc, _own, _aud = _svc(es_dueno=True)
        d = asyncio.run(
            svc.autorizar(7, _COMISIONISTA, ResourceType.DESAFIO_OOB, AccionRecurso.RESOLVE, "d1")
        )
        assert d.permitido is True

    def test_ajeno_denegado_404(self) -> None:
        svc, _own, _aud = _svc(es_dueno=False)
        d = asyncio.run(
            svc.autorizar(7, _COMISIONISTA, ResourceType.DESAFIO_OOB, AccionRecurso.RESOLVE, "d1")
        )
        assert d.permitido is False
        assert d.status == 404


class TestFirmaAutoservicio:
    def test_cualquier_autenticado_permitido(self) -> None:
        svc, own, _aud = _svc(es_dueno=False)
        d = asyncio.run(
            svc.autorizar(
                7, _COMISIONISTA, ResourceType.EVIDENCIA_FIRMA, AccionRecurso.CREATE, None
            )
        )
        assert d.permitido is True
        assert own.consultado is False


class TestModos:
    def test_audit_registra_pero_deja_pasar(self) -> None:
        svc, _own, aud = _svc(es_dueno=False, modo="audit")
        d = asyncio.run(
            svc.autorizar(7, _COMISIONISTA, ResourceType.DOCUMENTO, AccionRecurso.CREATE, "999")
        )
        assert d.permitido is True
        assert aud.registros[-1] == (False, "ownership", "audit")

    def test_off_permite_sin_evaluar(self) -> None:
        svc, own, aud = _svc(es_dueno=False, modo="off")
        d = asyncio.run(
            svc.autorizar(7, _COMISIONISTA, ResourceType.DOCUMENTO, AccionRecurso.CREATE, "999")
        )
        assert d.permitido is True
        assert own.consultado is False
        assert aud.registros == []


class TestReglas:
    def test_rol_sin_permiso_denegado(self) -> None:
        # teleperformance no tiene DOCUMENTOS_SUBIR_PROPIO ni MODERAR.
        svc, _own, _aud = _svc(es_dueno=True)
        d = asyncio.run(
            svc.autorizar(
                7,
                frozenset({RolUsuario.TELEPERFORMANCE}),
                ResourceType.DOCUMENTO,
                AccionRecurso.CREATE,
                "123",
            )
        )
        assert d.permitido is False
        assert d.status == 403
        assert _aud.registros[-1][1] == "rol"

    def test_par_sin_politica_denegado(self) -> None:
        svc, _own, _aud = _svc(es_dueno=True)
        d = asyncio.run(
            svc.autorizar(7, _COMISIONISTA, ResourceType.EVIDENCIA_FIRMA, AccionRecurso.DELETE, "123")
        )
        assert d.permitido is False
        assert _aud.registros[-1][1] == "sin-politica"
