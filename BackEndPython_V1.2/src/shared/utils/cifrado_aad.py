from __future__ import annotations


def construir_aad(tabla: str, columna: str, pk: str) -> str:
    """AAD canónico que liga un criptograma a su ubicación lógica.

    Debe construirse idéntico en la escritura (repositorio/backfill) y en la
    lectura (repositorio/reportes); cualquier divergencia hace fallar la
    verificación del tag GCM al descifrar.
    """
    return f"{tabla}|{columna}|{pk}"
