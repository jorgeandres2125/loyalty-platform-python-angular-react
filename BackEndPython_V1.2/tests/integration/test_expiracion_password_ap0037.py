from __future__ import annotations

from datetime import datetime, timedelta

from src.application.services.servicio_expiracion_password import (
    ServicioExpiracionPassword,
)
from src.domain.services.politica_expiracion_password import PoliticaExpiracionPassword
from src.infrastructure.external.in_memory_password_expiracion_repo import (
    InMemoryPasswordExpiracionRepo,
)

AHORA: datetime = datetime(2026, 7, 3, 12, 0, 0)


def _politica(vigencia: int = 90, aviso: int = 7) -> PoliticaExpiracionPassword:
    return PoliticaExpiracionPassword(vigencia_dias=vigencia, aviso_dias=aviso)


class TestPolitica:
    def test_fecha_expiracion_es_cambio_mas_vigencia(self):
        cambiado = AHORA - timedelta(days=10)
        assert _politica().fecha_expiracion(cambiado) == cambiado + timedelta(days=90)

    def test_faltan_exactamente_7_dias(self):
        # Cambiada hace 83 dias, vigencia 90 -> vence en 7 dias exactos.
        cambiado = AHORA - timedelta(days=83)
        assert _politica().dias_restantes(cambiado, AHORA) == 7

    def test_faltan_horas_redondea_a_un_dia(self):
        # Vence en 12 horas -> 1 dia (manana).
        cambiado = AHORA - timedelta(days=90) + timedelta(hours=12)
        assert _politica().dias_restantes(cambiado, AHORA) == 1

    def test_fraccion_redondea_hacia_arriba(self):
        # Vence en 6 dias y 5 horas -> 7 dias.
        cambiado = AHORA - timedelta(days=84) + timedelta(hours=5)
        assert _politica().dias_restantes(cambiado, AHORA) == 7

    def test_ya_vencida_da_cero_o_negativo(self):
        cambiado = AHORA - timedelta(days=91)
        assert _politica().dias_restantes(cambiado, AHORA) <= 0

    def test_debe_avisar_solo_en_ventana(self):
        pol = _politica(aviso=7)
        assert pol.debe_avisar(7) is True
        assert pol.debe_avisar(1) is True
        assert pol.debe_avisar(8) is False
        assert pol.debe_avisar(0) is False
        assert pol.debe_avisar(-1) is False

    def test_evaluar_devuelve_aviso_dentro_de_ventana(self):
        cambiado = AHORA - timedelta(days=85)  # vence en 5 dias
        aviso = _politica().evaluar(cambiado, AHORA)
        assert aviso is not None
        assert aviso.dias_restantes == 5
        assert aviso.fecha_expiracion_iso == (cambiado + timedelta(days=90)).date().isoformat()

    def test_evaluar_devuelve_none_fuera_de_ventana(self):
        cambiado = AHORA - timedelta(days=10)  # vence en 80 dias
        assert _politica().evaluar(cambiado, AHORA) is None

    def test_evaluar_devuelve_none_si_ya_vencida(self):
        cambiado = AHORA - timedelta(days=200)
        assert _politica().evaluar(cambiado, AHORA) is None


class _RepoQueFalla:
    async def obtener_cambiado_en(self, uid: int):
        raise RuntimeError("BD caida (tabla ausente)")

    async def registrar_cambio(self, uid: int, cuando: datetime) -> None:
        raise RuntimeError("BD caida")

    async def asegurar_baseline(self, uid: int, cuando: datetime) -> None:
        raise RuntimeError("BD caida")


class TestServicio:
    async def test_sin_baseline_no_avisa(self):
        servicio = ServicioExpiracionPassword(
            repo=InMemoryPasswordExpiracionRepo(), politica=_politica()
        )
        assert await servicio.evaluar_aviso(1, AHORA) is None

    async def test_avisa_cuando_baseline_en_ventana(self):
        repo = InMemoryPasswordExpiracionRepo()
        await repo.registrar_cambio(1, AHORA - timedelta(days=85))  # vence en 5 dias
        servicio = ServicioExpiracionPassword(repo=repo, politica=_politica())
        aviso = await servicio.evaluar_aviso(1, AHORA)
        assert aviso is not None
        assert aviso.dias_restantes == 5

    async def test_deshabilitado_no_avisa_ni_escribe(self):
        repo = InMemoryPasswordExpiracionRepo()
        servicio = ServicioExpiracionPassword(
            repo=repo, politica=_politica(), habilitado=False
        )
        await servicio.asegurar_baseline(1, AHORA)
        assert await repo.obtener_cambiado_en(1) is None
        assert await servicio.evaluar_aviso(1, AHORA) is None

    async def test_asegurar_baseline_no_pisa_valor_existente(self):
        repo = InMemoryPasswordExpiracionRepo()
        original = AHORA - timedelta(days=40)
        await repo.registrar_cambio(1, original)
        servicio = ServicioExpiracionPassword(repo=repo, politica=_politica())
        await servicio.asegurar_baseline(1, AHORA)
        assert await repo.obtener_cambiado_en(1) == original

    async def test_registrar_cambio_reinicia_reloj(self):
        repo = InMemoryPasswordExpiracionRepo()
        await repo.registrar_cambio(1, AHORA - timedelta(days=85))
        servicio = ServicioExpiracionPassword(repo=repo, politica=_politica())
        assert await servicio.evaluar_aviso(1, AHORA) is not None  # avisaba
        await servicio.registrar_cambio(1, AHORA)  # reinicia
        assert await servicio.evaluar_aviso(1, AHORA) is None  # ya no avisa

    async def test_fail_safe_lectura_no_propaga(self):
        servicio = ServicioExpiracionPassword(repo=_RepoQueFalla(), politica=_politica())
        assert await servicio.evaluar_aviso(1, AHORA) is None

    async def test_fail_safe_escritura_no_propaga(self):
        servicio = ServicioExpiracionPassword(repo=_RepoQueFalla(), politica=_politica())
        await servicio.asegurar_baseline(1, AHORA)
        await servicio.registrar_cambio(1, AHORA)


class TestSchema:
    def test_me_response_serializa_password_aviso(self):
        from src.adapters.api.schemas.me_response_schema import MeResponse
        from src.adapters.api.schemas.password_aviso_schema import PasswordAvisoSchema

        me = MeResponse(
            uid=1,
            username="jdoe",
            email="jdoe@sufi.test",
            roles=["comisionista"],
            tiene_incentivos=False,
            programa=1,
            password_aviso=PasswordAvisoSchema(
                dias_restantes=7, fecha_expiracion="2026-09-30"
            ),
        )
        data = me.model_dump()
        assert data["password_aviso"]["dias_restantes"] == 7
        assert data["password_aviso"]["fecha_expiracion"] == "2026-09-30"

    def test_me_response_password_aviso_por_defecto_none(self):
        from src.adapters.api.schemas.me_response_schema import MeResponse

        me = MeResponse(
            uid=1,
            username="jdoe",
            email="jdoe@sufi.test",
            roles=[],
            tiene_incentivos=False,
            programa=None,
        )
        assert me.password_aviso is None
