from __future__ import annotations

import pytest

from src.domain.exceptions.email_invalido import EmailInvalido
from src.domain.value_objects.email import Email


def test_email_valido_normaliza_a_minusculas() -> None:
    assert Email("  Test@Example.COM ").valor == "test@example.com"


def test_email_valido_con_punto_y_mas() -> None:
    assert Email("a.b+c@mail.example.co").valor == "a.b+c@mail.example.co"


@pytest.mark.parametrize("malo", ["sinarroba", "a@", "@b.com", "a@b", "a b@c.com", ""])
def test_email_invalido_lanza(malo: str) -> None:
    with pytest.raises(EmailInvalido):
        Email(malo)


def test_es_str() -> None:
    assert str(Email("uno@dos.com")) == "uno@dos.com"
