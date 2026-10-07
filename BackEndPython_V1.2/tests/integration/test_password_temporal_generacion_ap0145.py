"""AP-0145: las contrasenas temporales deben generarse de forma automatica y aleatoria.

El subsistema de credencial temporal ya existe (AP-0046, AP-0047, AP-0048). Estas pruebas
blindan especificamente el requisito de AP-0145: que NO exista ninguna via para que un
administrador (o cualquier otro emisor) defina manualmente el valor de una temporal, y que el
generador produzca claves aleatorias, unicas y sin colisiones a lo largo de muchas emisiones.
"""
from __future__ import annotations

import inspect

import pytest
from pydantic import ValidationError

from src.adapters.api.schemas.admin.usuarios.password_temporal_request import (
    PasswordTemporalRequest,
)
from src.application.services.servicio_password_temporal import ServicioPasswordTemporal
from src.application.use_cases.emitir_password_temporal_use_case import (
    EmitirPasswordTemporalUseCase,
)
from src.domain.services.politica_password_temporal import PoliticaPasswordTemporal
from src.domain.value_objects.origen_password_temporal import OrigenPasswordTemporal
from src.infrastructure.external.in_memory_password_temporal_repo import (
    InMemoryPasswordTemporalRepo,
)
from src.infrastructure.security.password_hasher import PasswordHasher

_N_EMISIONES: int = 500


def _servicio() -> ServicioPasswordTemporal:
    return ServicioPasswordTemporal(
        repo=InMemoryPasswordTemporalRepo(),
        politica=PoliticaPasswordTemporal(ttl_minutos=120),
        hasher=PasswordHasher(),
    )


class TestSinViaManual:
    """AP-0145: ninguna contrasena temporal puede ser definida manualmente."""

    @pytest.mark.parametrize(
        "campo_intruso", ["password", "clave", "temporal", "new_pass", "valor"]
    )
    def test_request_de_emision_rechaza_cualquier_campo_de_password(
        self, campo_intruso: str
    ) -> None:
        with pytest.raises(ValidationError):
            PasswordTemporalRequest.model_validate(
                {"origen": "admin", campo_intruso: "loquesea123"}
            )

    def test_request_de_emision_solo_admite_origen_y_motivo(self) -> None:
        campos: set[str] = set(PasswordTemporalRequest.model_fields.keys())
        assert campos == {"origen", "motivo"}

    def test_caso_de_uso_de_emision_no_recibe_password_como_parametro(self) -> None:
        # AP-0145: si algun dia alguien agrega un parametro de password aqui, esta
        # prueba lo detecta antes de que llegue a produccion.
        firma = inspect.signature(EmitirPasswordTemporalUseCase.ejecutar_async)
        nombres_parametros: set[str] = set(firma.parameters.keys()) - {"self"}
        assert not any(
            "pass" in nombre or "clave" in nombre for nombre in nombres_parametros
        ), nombres_parametros

    def test_servicio_emitir_no_recibe_password_como_parametro(self) -> None:
        firma = inspect.signature(ServicioPasswordTemporal.emitir)
        nombres_parametros: set[str] = set(firma.parameters.keys()) - {"self"}
        assert not any(
            "pass" in nombre or "clave" in nombre for nombre in nombres_parametros
        ), nombres_parametros

    async def test_emitir_siempre_produce_una_clave_generada_por_el_sistema(self) -> None:
        servicio = _servicio()
        entidad, clave = await servicio.emitir(
            uid=1,
            emitida_por_uid=99,
            emitida_por_usuario="admin",
            origen=OrigenPasswordTemporal.ADMIN,
        )
        # La unica forma de que la clave devuelta sea valida es que provenga del
        # generador: se verifica contra el hash persistido (no hay atajo posible).
        assert PasswordHasher().verificar(clave, entidad.hash_temporal)
        assert len(clave) == 16


class TestAleatoriedadYUnicidad:
    """AP-0145: generacion automatica con CSPRNG, sin reutilizacion ni colisiones."""

    def test_n_generaciones_son_todas_distintas(self) -> None:
        servicio = _servicio()
        claves: list[str] = [servicio.generar_clave() for _ in range(_N_EMISIONES)]
        assert len(set(claves)) == _N_EMISIONES

    def test_no_hay_patron_secuencial_ni_prefijo_comun(self) -> None:
        servicio = _servicio()
        claves: list[str] = [servicio.generar_clave() for _ in range(50)]
        primeros_caracteres: set[str] = {clave[0] for clave in claves}
        # Con CSPRNG sobre un alfabeto de 54 simbolos, 50 muestras no deberian
        # colapsar todas al mismo caracter inicial (indicaria un generador roto).
        assert len(primeros_caracteres) > 1

    async def test_emisiones_sucesivas_para_el_mismo_usuario_no_se_repiten(self) -> None:
        servicio = _servicio()
        claves: set[str] = set()
        for _ in range(20):
            _entidad, clave = await servicio.emitir(
                uid=1,
                emitida_por_uid=99,
                emitida_por_usuario="admin",
                origen=OrigenPasswordTemporal.ADMIN,
            )
            claves.add(clave)
        assert len(claves) == 20

    def test_entropia_minima_por_clase_garantizada(self) -> None:
        servicio = _servicio()
        for _ in range(100):
            clave: str = servicio.generar_clave()
            minuscula = sum(1 for c in clave if c.islower())
            mayuscula = sum(1 for c in clave if c.isupper())
            digito = sum(1 for c in clave if c.isdigit())
            assert minuscula >= 2
            assert mayuscula >= 2
            assert digito >= 2
