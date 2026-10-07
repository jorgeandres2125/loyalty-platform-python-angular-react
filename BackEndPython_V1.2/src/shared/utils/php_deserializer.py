from __future__ import annotations

import json
from typing import Any, Final

# AP-0115: el parser solo procesa datos (escalares y arrays); jamas instancia
# objetos. Estos topes evitan agotamiento de pila o memoria y los tipos de
# objeto y referencia de PHP (vector de inyeccion) se rechazan explicitamente.
_MAX_PROFUNDIDAD: Final[int] = 64
_MAX_BYTES: Final[int] = 1_000_000
_TIPOS_PHP_PROHIBIDOS: Final[frozenset[str]] = frozenset(
    {"O", "C", "R", "r", "S"}
)


def parse_php_serialized(raw: str | None) -> str | None:
    """
    Convierte un string PHP-serializado heredado de Drupal a JSON.

    Casos soportados:
    - ``a:0:{}``               → ``"[]"``
    - PHP set (clave==valor)   → ``'["val1","val2"]'``
    - Array indexado de objs   → ``'[{"nombre":"…","genero":"M",…}]'``
    - String plano / None      → se devuelve sin cambios
    """
    if not raw or not raw.startswith("a:"):
        return raw
    datos: bytes = raw.encode("utf-8")
    if len(datos) > _MAX_BYTES:
        return raw
    try:
        value, _ = _parse_value(datos, 0, 0)
        if not isinstance(value, dict):
            return raw

        keys: list[Any] = list(value.keys())

        # Array indexado PHP (i:0;, i:1;, …) → lista JSON
        if (
            keys
            and all(isinstance(clave, int) for clave in keys)
            and keys == list(range(len(keys)))
        ):
            items: list[Any] = [value[i] for i in range(len(keys))]
            return json.dumps(items, ensure_ascii=False)

        # PHP set (clave == valor): extraer valores únicos en orden
        return json.dumps(
            list(dict.fromkeys(str(valor) for valor in value.values())),
            ensure_ascii=False,
        )
    except Exception:
        return raw


def _parse_value(data: bytes, pos: int, depth: int) -> tuple[Any, int]:
    if depth > _MAX_PROFUNDIDAD:
        raise ValueError("profundidad de estructura PHP excede el limite seguro")
    type_char: str = chr(data[pos])

    if type_char in _TIPOS_PHP_PROHIBIDOS:
        raise ValueError(
            "tipo PHP inseguro deshabilitado (AP-0115): "
            "objetos y referencias no se deserializan"
        )

    if type_char == "N":
        return None, pos + 2  # N;

    if type_char == "b":
        return data[pos + 2] == ord("1"), pos + 4  # b:0; or b:1;

    if type_char == "i":
        end: int = data.index(b";", pos)
        return int(data[pos + 2 : end]), end + 1

    if type_char == "d":
        end = data.index(b";", pos)
        return float(data[pos + 2 : end]), end + 1

    if type_char == "s":
        # s:N:"<N bytes>";
        colon: int = data.index(b":", pos + 2)
        length: int = int(data[pos + 2 : colon])
        str_start: int = colon + 2  # saltar :"
        if length < 0 or str_start + length > len(data):
            raise ValueError("longitud de string PHP fuera de rango")
        str_bytes: bytes = data[str_start : str_start + length]
        return str_bytes.decode("utf-8", errors="replace"), str_start + length + 2  # saltar ";

    if type_char == "a":
        # a:N:{…}
        colon = data.index(b":", pos + 2)
        count: int = int(data[pos + 2 : colon])
        cur: int = colon + 2  # saltar :{
        result: dict[Any, Any] = {}
        for _ in range(count):
            key, cur = _parse_value(data, cur, depth + 1)
            val, cur = _parse_value(data, cur, depth + 1)
            result[key] = val
        return result, cur + 1  # saltar }

    raise ValueError(f"Tipo PHP desconocido '{type_char}' en posición {pos}")


def to_php_serialized_set(values: list[str] | None) -> str | None:
    """
    Serializa una lista de strings al formato PHP "set" (clave == valor)
    usado por Drupal: ``a:N:{s:LEN:"v";s:LEN:"v";...}``.

    - Devuelve ``None`` si la entrada es ``None`` o vacía.
    - ``LEN`` es la longitud en bytes UTF-8 (consistente con el formato legado).
    """
    if not values:
        return None
    parts: list[str] = []
    for raw_value in values:
        text: str = str(raw_value)
        byte_len: int = len(text.encode("utf-8"))
        parts.append(f's:{byte_len}:"{text}";s:{byte_len}:"{text}";')
    return f"a:{len(values)}:{{{''.join(parts)}}}"


def json_to_php_serialized_set(raw: str | None) -> str | None:
    """
    Convierte un string JSON-array (formato del frontend) al formato PHP
    serializado heredado de Drupal.

    - ``None`` o cadena vacía → ``None``.
    - Cadena que ya empieza por ``"a:"`` → se devuelve sin cambios.
    - JSON array (``["v1","v2"]``) → ``a:N:{s:LEN:"v1";s:LEN:"v1";...}``.
    - Cualquier otro contenido se devuelve tal cual.
    """
    if not raw:
        return None
    stripped: str = raw.strip()
    if not stripped:
        return None
    if stripped.startswith("a:"):
        return raw
    try:
        data: Any = json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        return raw
    if isinstance(data, list):
        return to_php_serialized_set([str(valor) for valor in data])
    return raw


def to_php_serialized(value: Any) -> str:
    """
    Serializa un valor Python al formato PHP ``serialize()``.

    Tipos soportados: ``None``, ``bool``, ``int``, ``float``, ``str``,
    ``list`` (array indexado), ``dict`` (array asociativo).

    Las longitudes de strings se calculan en bytes UTF-8 para mantener
    compatibilidad con la representación legada de Drupal.
    """
    if value is None:
        return "N;"
    if isinstance(value, bool):
        return f"b:{1 if value else 0};"
    if isinstance(value, int):
        return f"i:{value};"
    if isinstance(value, float):
        return f"d:{value};"
    if isinstance(value, str):
        byte_len: int = len(value.encode("utf-8"))
        return f's:{byte_len}:"{value}";'
    if isinstance(value, list):
        list_parts: list[str] = []
        for index, item in enumerate(value):
            list_parts.append(f"i:{index};{to_php_serialized(item)}")
        return f"a:{len(value)}:{{{''.join(list_parts)}}}"
    if isinstance(value, dict):
        dict_parts: list[str] = []
        for key, val in value.items():
            key_serialized: str = (
                to_php_serialized(key)
                if isinstance(key, (int, str))
                else to_php_serialized(str(key))
            )
            val_serialized: str = to_php_serialized(val)
            dict_parts.append(f"{key_serialized}{val_serialized}")
        return f"a:{len(value)}:{{{''.join(dict_parts)}}}"
    raise ValueError(f"No se puede serializar el tipo {type(value).__name__}")


def json_to_php_serialized(raw: str | None) -> str | None:
    """
    Convierte cualquier estructura JSON (objeto, array, escalar) al formato
    PHP serializado.

    - ``None`` o cadena vacía → ``None``.
    - Cadena que ya empieza por ``"a:"``, ``"N;"``, ``"b:"``, ``"i:"``,
      ``"d:"`` o ``"s:"`` → se devuelve sin cambios (ya serializada).
    - JSON válido → se convierte vía :func:`to_php_serialized`.
    - Si ``json.loads`` falla, se devuelve la cadena original.
    """
    if not raw:
        return None
    stripped: str = raw.strip()
    if not stripped:
        return None
    if stripped[:2] in ("a:", "N;", "b:", "i:", "d:", "s:"):
        return raw
    try:
        data: Any = json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        return raw
    return to_php_serialized(data)
