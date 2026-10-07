"""BUG_TRIBUTARIO_COMISIONISTA_MOVILIDAD_001: el comisionista no veia sus PDF tributarios.

Causa raiz doble:
  (1) La pestana Tributario del perfil propio leia GET /documentos/{doc}, endpoint de staff
      (DOCUMENTOS_MODERAR) -> 403 para el dueno -> la lista quedaba vacia y ningun PDF se
      mostraba. Como admin si aparecian, de ahi la asimetria reportada.
  (2) El endpoint self-service /me/documentos/upload solo admitia los tipos {4,5,6}
      (Cedula, RUT, Contrato), dejando fuera TODOS los tributarios (EPS=7 .. Dependientes=14),
      por lo que la pestana no tenia forma legitima de gestionarlos como dueno.

Estas pruebas fijan el contrato: el self-service cubre el catalogo completo y no puede
volver a quedarse corto si se anade un tipo nuevo.
"""
from __future__ import annotations

from src.adapters.api.routers.me_router import _TIPOS_DOC_VALIDOS
from src.shared.constants.tipos_documento import (
    TIPOS_DOCUMENTO_NOMBRES,
    TIPOS_DOCUMENTO_PREFIJOS,
)

# Los 10 tipos que el comisionista de Movilidad gestiona desde PERFIL -> TRIBUTARIO.
_TIPOS_TRIBUTARIOS: dict[int, str] = {
    7: "EPS",
    8: "AFP / Pensiones (obligatoria)",
    9: "ARL",
    10: "Medicina Prepagada",
    11: "Certificado intereses de vivienda",
    12: "Pensión Voluntaria",
    13: "AFC",
    14: "Dependientes",
    4: "Cédula",
    5: "RUT",
}


class TestCatalogoSelfService:
    def test_el_self_service_admite_todos_los_tipos_del_catalogo(self) -> None:
        # Antes era frozenset({4, 5, 6}) y los tributarios quedaban fuera.
        assert _TIPOS_DOC_VALIDOS == frozenset(TIPOS_DOCUMENTO_PREFIJOS)

    def test_todos_los_tipos_tributarios_son_gestionables_por_el_dueno(self) -> None:
        faltantes: list[str] = [
            nombre
            for tipo, nombre in _TIPOS_TRIBUTARIOS.items()
            if tipo not in _TIPOS_DOC_VALIDOS
        ]
        assert not faltantes, faltantes

    def test_el_catalogo_no_se_desincroniza(self) -> None:
        # Si se anade un tipo nuevo con prefijo pero sin nombre (o al reves), el perfil
        # propio lo mostraria roto; el catalogo debe cubrir ambos mapas.
        assert set(TIPOS_DOCUMENTO_PREFIJOS) == set(TIPOS_DOCUMENTO_NOMBRES)

    def test_cada_tipo_tributario_tiene_prefijo_de_archivo(self) -> None:
        # El nombre del PDF se construye en el servidor como <prefijo><documento>.pdf.
        for tipo in _TIPOS_TRIBUTARIOS:
            assert TIPOS_DOCUMENTO_PREFIJOS[tipo].strip()
