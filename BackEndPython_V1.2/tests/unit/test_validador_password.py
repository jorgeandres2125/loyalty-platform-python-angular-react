from __future__ import annotations

import pytest

from src.domain.exceptions.password_insegura import PasswordInsegura
from src.domain.services.validador_password import ValidadorPassword
from src.shared.constants.password_blacklist import BLACKLIST_COMUNES


@pytest.fixture()
def validador() -> ValidadorPassword:
    return ValidadorPassword(blacklist=BLACKLIST_COMUNES)


class TestBlacklist:
    def test_contrasena_comun_rechazada(self, validador: ValidadorPassword) -> None:
        with pytest.raises(PasswordInsegura):
            validador.validar("123456")

    def test_contrasena_comun_mayusculas_rechazada(self, validador: ValidadorPassword) -> None:
        with pytest.raises(PasswordInsegura):
            validador.validar("PASSWORD")

    def test_admin_rechazado(self, validador: ValidadorPassword) -> None:
        with pytest.raises(PasswordInsegura):
            validador.validar("admin")

    def test_contrasena_fuerte_aceptada(self, validador: ValidadorPassword) -> None:
        validador.validar("Tr0mb0ne!Azul#2026")

    def test_en_blacklist_helper(self, validador: ValidadorPassword) -> None:
        assert validador.en_blacklist("password") is True
        assert validador.en_blacklist("Tr0mb0ne!Azul#2026") is False


class TestContextual:
    def test_igual_al_nombre_rechazado(self, validador: ValidadorPassword) -> None:
        with pytest.raises(PasswordInsegura):
            validador.validar("JuanPerez", valores_contextuales=["juanperez"])

    def test_contiene_nombre_rechazado(self, validador: ValidadorPassword) -> None:
        with pytest.raises(PasswordInsegura):
            validador.validar("JuanPerez123!", valores_contextuales=["JuanPerez"])

    def test_sin_contexto_aceptada(self, validador: ValidadorPassword) -> None:
        validador.validar("Tr0mb0ne!Azul#2026", valores_contextuales=None)

    def test_contexto_vacio_ignorado(self, validador: ValidadorPassword) -> None:
        validador.validar("Tr0mb0ne!Azul#2026", valores_contextuales=["", ""])

    def test_contrasena_fuerte_con_contexto_irrelevante(self, validador: ValidadorPassword) -> None:
        validador.validar("Tr0mb0ne!Azul#2026", valores_contextuales=["pedro", "99999999"])


class TestBlacklistIntegridad:
    def test_blacklist_no_vacia(self) -> None:
        assert len(BLACKLIST_COMUNES) > 50

    def test_blacklist_es_frozenset(self) -> None:
        assert isinstance(BLACKLIST_COMUNES, frozenset)

    def test_contrasenas_criticas_presentes(self) -> None:
        criticas = {"123456", "password", "admin", "qwerty", "letmein", "iloveyou"}
        assert criticas.issubset(BLACKLIST_COMUNES)
