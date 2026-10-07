from __future__ import annotations

from urllib.parse import unquote_plus


def colapsar_parametros_duplicados(
    query_string: bytes, nombres_multivalor: frozenset[str]
) -> tuple[bytes, list[str]]:
    """AP-0199: descarta apariciones repetidas de parametros de query cuyo
    nombre no esta definido como multi-valor, conservando SOLO la primera.

    Opera sobre el query_string crudo (bytes del scope ASGI) sin re-codificar los
    tokens conservados: cada token que se conserva queda byte-a-byte identico
    al de entrada. Un nombre presente en nombres_multivalor puede repetirse libre.

    Devuelve el query_string normalizado y la lista (orden de aparicion, sin
    duplicados) de los nombres que llegaron repetidos, para auditoria. Si no hubo
    parametros repetidos, devuelve el query_string original sin cambios.
    """
    if not query_string:
        return query_string, []
    vistos: set[str] = set()
    duplicados: list[str] = []
    conservados: list[bytes] = []
    for token in query_string.split(b"&"):
        if not token:
            continue
        nombre_crudo: bytes = token.split(b"=", 1)[0]
        nombre: str = unquote_plus(nombre_crudo.decode("latin-1"))
        if nombre in nombres_multivalor:
            conservados.append(token)
            continue
        if nombre in vistos:
            if nombre not in duplicados:
                duplicados.append(nombre)
            continue
        vistos.add(nombre)
        conservados.append(token)
    if not duplicados:
        return query_string, []
    return b"&".join(conservados), duplicados
