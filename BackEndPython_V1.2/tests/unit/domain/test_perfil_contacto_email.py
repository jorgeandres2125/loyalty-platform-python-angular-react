from __future__ import annotations

from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity


def test_perfil_contacto_entity_tiene_campo_email() -> None:
    entity = PerfilContactoEntity(numero_documento="12345678", email="test@example.com")
    assert entity.email == "test@example.com"


def test_perfil_contacto_entity_email_opcional() -> None:
    entity = PerfilContactoEntity(numero_documento="12345678")
    assert entity.email is None
