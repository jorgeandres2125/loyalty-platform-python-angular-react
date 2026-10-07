from __future__ import annotations

from datetime import date

import pytest

from src.application.use_cases.asesor_consumo_use_case import AsesorConsumoUseCase
from src.application.use_cases.asesor_movilidad_use_case import AsesorMovilidadUseCase
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.entities.perfil_emocional_entity import PerfilEmocionalEntity
from src.domain.entities.perfil_tributario_entity import PerfilTributarioEntity
from src.domain.exceptions.paso_omitido import PasoOmitido

_ND = "111"


class _FakeRepo:
    def __init__(self, contacto=False, tributario=False, emocional=False) -> None:
        self._contacto = PerfilContactoEntity(numero_documento=_ND) if contacto else None
        self._tributario = object() if tributario else None
        self._emocional = object() if emocional else None
        self.guardado_tributario = None
        self.guardado_emocional = None
        self.guardado_contacto = None

    async def obtener_contacto_async(self, nd):
        return self._contacto

    async def obtener_tributario_async(self, nd):
        return self._tributario

    async def obtener_emocional_async(self, nd):
        return self._emocional

    async def numero_documento_por_email_async(self, email):
        return None

    async def guardar_contacto_async(self, e):
        self.guardado_contacto = e
        return e

    async def guardar_tributario_async(self, e):
        self.guardado_tributario = e
        return e

    async def guardar_emocional_async(self, e):
        self.guardado_emocional = e
        return e


def _mov(repo) -> AsesorMovilidadUseCase:
    return AsesorMovilidadUseCase(asesor_repo=object(), perfil_repo=repo)  # type: ignore[arg-type]


def _con(repo) -> AsesorConsumoUseCase:
    return AsesorConsumoUseCase(asesor_repo=object(), perfil_repo=repo)  # type: ignore[arg-type]


class TestOrdenPasosMovilidad:
    async def test_paso2_sin_paso1_lanza(self) -> None:
        with pytest.raises(PasoOmitido):
            await _mov(_FakeRepo()).guardar_paso2_async(PerfilTributarioEntity(numero_documento=_ND))

    async def test_paso2_con_paso1_ok(self) -> None:
        repo = _FakeRepo(contacto=True)
        await _mov(repo).guardar_paso2_async(PerfilTributarioEntity(numero_documento=_ND))
        assert repo.guardado_tributario is not None

    async def test_paso3_sin_paso2_lanza(self) -> None:
        with pytest.raises(PasoOmitido):
            await _mov(_FakeRepo(contacto=True)).guardar_paso3_async(PerfilEmocionalEntity(numero_documento=_ND))

    async def test_paso3_con_previos_ok(self) -> None:
        repo = _FakeRepo(contacto=True, tributario=True)
        await _mov(repo).guardar_paso3_async(PerfilEmocionalEntity(numero_documento=_ND))
        assert repo.guardado_emocional is not None

    async def test_finalizar_sin_paso3_lanza(self) -> None:
        with pytest.raises(PasoOmitido):
            await _mov(_FakeRepo(contacto=True, tributario=True)).finalizar_async(_ND)

    async def test_finalizar_completo_ok(self) -> None:
        repo = _FakeRepo(contacto=True, tributario=True, emocional=True)
        res = await _mov(repo).finalizar_async(_ND)
        assert res.fecha_completado == date.today()


class TestOrdenPasosConsumo:
    async def test_paso3_sin_paso1_lanza(self) -> None:
        with pytest.raises(PasoOmitido):
            await _con(_FakeRepo()).guardar_paso3_async(PerfilEmocionalEntity(numero_documento=_ND))

    async def test_finalizar_sin_emocional_lanza(self) -> None:
        with pytest.raises(PasoOmitido):
            await _con(_FakeRepo(contacto=True)).finalizar_async(_ND)

    async def test_finalizar_completo_ok(self) -> None:
        repo = _FakeRepo(contacto=True, emocional=True)
        res = await _con(repo).finalizar_async(_ND)
        assert res.fecha_completado == date.today()
