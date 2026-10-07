"""AP-0115: el deserializador PHP legacy es seguro y robusto.

No instancia objetos (rechaza tipos O/C/R/r/S), aplica limites de profundidad y
tamano, valida longitudes de string y ante cualquier anomalia devuelve el raw
(fail-safe). Las entradas se construyen con chr(58) para los dos puntos.
"""
from __future__ import annotations

import pytest

from src.shared.utils.php_deserializer import (
    _MAX_BYTES,
    _MAX_PROFUNDIDAD,
    _parse_value,
    parse_php_serialized,
    to_php_serialized,
    to_php_serialized_set,
)

C = chr(58)
DQ = chr(34)


def test_parsea_set_valido_exacto() -> None:
    raw = to_php_serialized_set(["abc", "xyz"])
    esperado = "[" + DQ + "abc" + DQ + ", " + DQ + "xyz" + DQ + "]"
    assert parse_php_serialized(raw) == esperado


def test_parsea_array_indexado_de_objetos() -> None:
    raw = to_php_serialized([{"nombre": "Ana"}])
    esperado = "[{" + DQ + "nombre" + DQ + ": " + DQ + "Ana" + DQ + "}]"
    assert parse_php_serialized(raw) == esperado


def test_rechaza_objeto_php() -> None:
    mal = ("O" + C + "8" + C + DQ + "stdClass" + DQ + C + "0" + C + "{}").encode()
    with pytest.raises(ValueError):
        _parse_value(mal, 0, 0)


def test_objeto_envuelto_devuelve_raw_failsafe() -> None:
    payload = (
        "a" + C + "1" + C + "{i" + C + "0;O" + C + "1" + C
        + DQ + "X" + DQ + C + "0" + C + "{}}"
    )
    assert parse_php_serialized(payload) == payload


def test_rechaza_referencia_php() -> None:
    ref = ("R" + C + "1;").encode()
    with pytest.raises(ValueError):
        _parse_value(ref, 0, 0)


def test_limite_de_profundidad() -> None:
    with pytest.raises(ValueError):
        _parse_value(b"N;", 0, _MAX_PROFUNDIDAD + 1)


def test_limite_de_tamano_devuelve_raw() -> None:
    grande = "a" + C + "0" + C + "{}" + ("z" * (_MAX_BYTES + 10))
    assert parse_php_serialized(grande) == grande


def test_string_fuera_de_rango_es_failsafe() -> None:
    mal = "a" + C + "1" + C + "{s" + C + "99" + C + DQ + "x" + DQ + ";}"
    assert parse_php_serialized(mal) == mal


def test_string_plano_y_none_sin_cambios() -> None:
    assert parse_php_serialized("hola mundo") == "hola mundo"
    assert parse_php_serialized(None) is None


def test_roundtrip_set_unicos() -> None:
    raw = to_php_serialized_set(["uno", "dos", "uno"])
    esperado = "[" + DQ + "uno" + DQ + ", " + DQ + "dos" + DQ + "]"
    assert parse_php_serialized(raw) == esperado
