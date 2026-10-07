from __future__ import annotations


class InMemoryPasswordHistoryRepo:
    """AP-0041: adaptador en memoria del historial de contrasenas (para pruebas).

    Satisface PasswordHistoryRepository (PEP 544). Guarda por uid una lista de pares
    (hash, creado_iso). El adaptador durable de produccion es el SQL.
    """

    def __init__(self) -> None:
        self._filas: dict[int, list[tuple[str, str]]] = {}

    async def ultimos_hashes(self, uid: int, cantidad: int) -> list[str]:
        filas = sorted(
            self._filas.get(uid, []), key=lambda par: par[1], reverse=True
        )
        return [hash_valor for hash_valor, _ in filas[:cantidad]]

    async def insertar(self, uid: int, password_hash: str, creado_iso: str) -> None:
        self._filas.setdefault(uid, []).append((password_hash, creado_iso))

    async def podar(self, uid: int, conservar: int) -> None:
        filas = sorted(
            self._filas.get(uid, []), key=lambda par: par[1], reverse=True
        )
        self._filas[uid] = filas[:conservar]
