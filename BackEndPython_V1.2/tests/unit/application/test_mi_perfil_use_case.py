"""Tests para MiPerfilUseCase (self-edit del propio comisionista)."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.mi_perfil_use_case import MiPerfilUseCase
from src.domain.entities.documento_entity import DocumentoEntity
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.entities.perfil_emocional_entity import PerfilEmocionalEntity
from src.domain.entities.perfil_tributario_entity import PerfilTributarioEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.perfil_no_encontrado import PerfilNoEncontrado


def _usuario(uid: int = 551, nombre: str = "1129565843") -> UsuarioEntity:
    return UsuarioEntity(uid=uid, nombre=nombre, email="x@y.co", roles=[], activo=True)


def _make_uc(
    usuario: UsuarioEntity | None = _usuario(),
    contacto: PerfilContactoEntity | None = None,
    tributario: PerfilTributarioEntity | None = None,
    emocional: PerfilEmocionalEntity | None = None,
    documentos: list[DocumentoEntity] | None = None,
) -> MiPerfilUseCase:
    usuario_repo = AsyncMock()
    usuario_repo.obtener_por_uid_async.return_value = usuario
    perfil_repo = AsyncMock()
    perfil_repo.obtener_contacto_async.return_value = contacto
    perfil_repo.obtener_tributario_async.return_value = tributario
    perfil_repo.obtener_emocional_async.return_value = emocional
    perfil_repo.guardar_contacto_async.side_effect = lambda e: e
    perfil_repo.guardar_tributario_async.side_effect = lambda e: e
    perfil_repo.guardar_emocional_async.side_effect = lambda e: e
    documento_repo = AsyncMock()
    documento_repo.listar_por_asesor_async.return_value = documentos or []
    return MiPerfilUseCase(
        usuario_repo=usuario_repo,
        perfil_repo=perfil_repo,
        documento_repo=documento_repo,
    )


# ── resolver_numero_documento ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resolver_numero_documento_retorna_users_name() -> None:
    """dbo.users.name == numero_documento para comisionistas."""
    uc = _make_uc(usuario=_usuario(uid=551, nombre="1129565843"))
    assert await uc.resolver_numero_documento_async(551) == "1129565843"


@pytest.mark.asyncio
async def test_resolver_numero_documento_lanza_si_usuario_no_existe() -> None:
    uc = _make_uc(usuario=None)
    with pytest.raises(PerfilNoEncontrado):
        await uc.resolver_numero_documento_async(999)


# ── guardar_contacto sobreescribe el numero_documento del JWT ──────────────

@pytest.mark.asyncio
async def test_guardar_contacto_ignora_numero_documento_del_body() -> None:
    """El usuario no puede usar el body para editar perfiles ajenos."""
    uc = _make_uc(usuario=_usuario(uid=551, nombre="1129565843"))
    entrada = PerfilContactoEntity(numero_documento="ATAQUE-9999999999")
    saved = await uc.guardar_contacto_async(uid=551, entity=entrada)
    assert saved.numero_documento == "1129565843"


@pytest.mark.asyncio
async def test_guardar_emocional_ignora_numero_documento_del_body() -> None:
    uc = _make_uc(usuario=_usuario(uid=551, nombre="1129565843"))
    entrada = PerfilEmocionalEntity(numero_documento="OTRO")
    saved = await uc.guardar_emocional_async(uid=551, entity=entrada)
    assert saved.numero_documento == "1129565843"


# ── Dashboard agregado ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dashboard_movilidad_calcula_porcentaje_3_stages() -> None:
    contacto = PerfilContactoEntity(
        numero_documento="1129565843",
        nombre_completo="Karen",
        celular="3001112233",
        direccion="Calle 1",
        comisionista_programa_id=1,
        incentivos=True,
    )
    tributario = PerfilTributarioEntity(numero_documento="1129565843", total=1500000)
    emocional = PerfilEmocionalEntity(numero_documento="1129565843", estado_civil="casado")
    uc = _make_uc(contacto=contacto, tributario=tributario, emocional=emocional)

    res = await uc.obtener_dashboard_async(uid=551, roles=["comisionista"])

    assert res["rol_principal"] == "comisionista"
    assert res["perfil"]["stages_total"] == 3
    assert res["perfil"]["stages_completos"] == 3
    assert res["perfil"]["porcentaje_completado"] == 100
    assert res["perfil"]["tributario_completo"] is True
    assert res["incentivos_habilitados"] is True
    assert res["programa"] == {"cpid": 1, "nombre": "Movilidad"}


@pytest.mark.asyncio
async def test_dashboard_consumo_no_calcula_tributario() -> None:
    """Para comisionista consumo, tributario_completo debe ser None y stages_total=2."""
    contacto = PerfilContactoEntity(
        numero_documento="39452431",
        nombre_completo="Liliana",
        celular="3009998877",
        direccion="Cra 2",
        comisionista_programa_id=2,
    )
    emocional = PerfilEmocionalEntity(numero_documento="39452431", estado_civil="soltero")
    uc = _make_uc(
        usuario=_usuario(uid=5691, nombre="39452431"),
        contacto=contacto,
        tributario=None,
        emocional=emocional,
    )

    res = await uc.obtener_dashboard_async(uid=5691, roles=["comisionista_consumo"])

    assert res["rol_principal"] == "comisionista_consumo"
    assert res["perfil"]["tributario_completo"] is None
    assert res["perfil"]["stages_total"] == 2
    assert res["perfil"]["stages_completos"] == 2
    assert res["perfil"]["porcentaje_completado"] == 100
    assert res["documentos"] is None
    assert res["programa"] == {"cpid": 2, "nombre": "Consumo y Servicios"}


@pytest.mark.asyncio
async def test_dashboard_movilidad_documentos_marca_subidos_y_aprobados() -> None:
    contacto = PerfilContactoEntity(
        numero_documento="X", comisionista_programa_id=1,
    )
    docs = [
        DocumentoEntity(numero_documento="X", nombre="cedula.pdf", estado="aprobado", version=2, fecha=None, tipo=4, did=1),
        DocumentoEntity(numero_documento="X", nombre="rut.pdf", estado="pendiente", version=1, fecha=None, tipo=5, did=2),
    ]
    uc = _make_uc(contacto=contacto, documentos=docs)

    res = await uc.obtener_dashboard_async(uid=551, roles=["comisionista"])

    docs_info = res["documentos"]
    assert docs_info is not None
    assert docs_info["total_subidos"] == 2
    assert docs_info["total_esperados"] == 3
    assert docs_info["total_aprobados"] == 1
    assert docs_info["items"]["cedula"]["subido"] is True
    assert docs_info["items"]["cedula"]["version"] == 2
    assert docs_info["items"]["rut"]["estado"] == "pendiente"
    assert docs_info["items"]["contrato"]["subido"] is False


@pytest.mark.asyncio
async def test_dashboard_porcentaje_0_si_no_hay_datos() -> None:
    uc = _make_uc(contacto=None, tributario=None, emocional=None)
    res = await uc.obtener_dashboard_async(uid=551, roles=["comisionista"])
    assert res["perfil"]["porcentaje_completado"] == 0
    assert res["perfil"]["stages_completos"] == 0
    assert res["nombre_completo"] == ""
    assert res["programa"] is None
