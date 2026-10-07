from __future__ import annotations

from src.domain.entities.profesion_entity import ProfesionEntity


def test_profesion_entity_crea_con_campos_correctos() -> None:
    entidad = ProfesionEntity(tid=3119, nombre="Abogado")
    assert entidad.tid == 3119
    assert entidad.nombre == "Abogado"


def test_profesion_entity_nombre_vacio() -> None:
    entidad = ProfesionEntity(tid=1, nombre="")
    assert entidad.nombre == ""
