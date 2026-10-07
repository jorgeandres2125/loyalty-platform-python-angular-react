from __future__ import annotations

import pytest

from src.application.use_cases.asesor_movilidad_use_case import AsesorMovilidadUseCase
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.exceptions.email_invalido import EmailInvalido
from src.domain.exceptions.email_no_unico import EmailNoUnico


class _FakePerfilRepo:
    def __init__(self, propietario: str | None) -> None:
        self._propietario = propietario
        self.guardado: PerfilContactoEntity | None = None

    async def numero_documento_por_email_async(self, email: str) -> str | None:
        return self._propietario

    async def guardar_contacto_async(self, entity: PerfilContactoEntity) -> PerfilContactoEntity:
        self.guardado = entity
        return entity


def _uc(propietario: str | None) -> AsesorMovilidadUseCase:
    return AsesorMovilidadUseCase(asesor_repo=object(), perfil_repo=_FakePerfilRepo(propietario))  # type: ignore[arg-type]


async def test_correo_nuevo_se_guarda_normalizado() -> None:
    uc = _uc(None)
    ent = PerfilContactoEntity(numero_documento="111", email="Nuevo@Mail.com")
    res = await uc.guardar_paso1_async(ent)
    assert res.email == "nuevo@mail.com"


async def test_correo_duplicado_de_otro_documento_lanza() -> None:
    uc = _uc("999")
    ent = PerfilContactoEntity(numero_documento="111", email="dup@mail.com")
    with pytest.raises(EmailNoUnico):
        await uc.guardar_paso1_async(ent)


async def test_correo_del_mismo_documento_se_permite() -> None:
    uc = _uc("111")
    ent = PerfilContactoEntity(numero_documento="111", email="mismo@mail.com")
    res = await uc.guardar_paso1_async(ent)
    assert res.email == "mismo@mail.com"


async def test_correo_invalido_lanza() -> None:
    uc = _uc(None)
    ent = PerfilContactoEntity(numero_documento="111", email="no-es-correo")
    with pytest.raises(EmailInvalido):
        await uc.guardar_paso1_async(ent)


async def test_sin_correo_se_guarda() -> None:
    uc = _uc("999")
    ent = PerfilContactoEntity(numero_documento="111", email=None)
    res = await uc.guardar_paso1_async(ent)
    assert res.numero_documento == "111"
