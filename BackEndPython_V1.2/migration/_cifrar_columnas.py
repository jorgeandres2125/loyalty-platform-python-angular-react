"""Motor genérico de cifrado a nivel de aplicación de columnas de texto de
users_perfil_contacto (Medida C — AP-0147 / AP-0095).

Driven por una lista de columnas. Para cada `col` (str/nvarchar en claro):
    F0 add     -> añade col_enc VARBINARY(MAX) si no existe
    F2 backfill-> cifra col -> col_enc (AES-256-GCM, AAD = tabla|col|numero_documento)
    F3 verify  -> paridad de conteos por columna + muestreo de descifrado == claro
    F4 drop    -> elimina la columna en claro (IRREVERSIBLE; exige F3 OK)

La clave se toma de Settings (APP_ENCRYPTION_KEY); no se hardcodea ni se imprime.
"""
from __future__ import annotations

import base64
from typing import Final

from sqlalchemy import Engine, text

from migration._common import TARGET_DB, sync_engine
from src.infrastructure.config.settings import Settings
from src.infrastructure.security.aes_gcm_field_cipher import AesGcmFieldCipher
from src.shared.constants.cifrado import TABLA_PERFIL_CONTACTO
from src.shared.utils.cifrado_aad import construir_aad

TABLA: Final[str] = TABLA_PERFIL_CONTACTO
BATCH: Final[int] = 1000


def build_cipher() -> AesGcmFieldCipher:
    settings: Settings = Settings()
    if not settings.app_encryption_key:
        raise SystemExit("APP_ENCRYPTION_KEY no configurada en el entorno — abortando")
    kid: int = settings.app_encryption_key_id
    return AesGcmFieldCipher({kid: base64.b64decode(settings.app_encryption_key)}, kid)


def _columna_existe(engine: Engine, columna: str) -> bool:
    sql: str = (
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_NAME = :t AND COLUMN_NAME = :c"
    )
    with engine.connect() as conn:
        total: int = conn.execute(text(sql), {"t": TABLA, "c": columna}).scalar_one()
    return total > 0


def f0_add(engine: Engine, columnas: list[str]) -> None:
    print("[F0] añadiendo columnas _enc VARBINARY(MAX)…")
    # El chequeo abre su propia conexión; debe ir FUERA del begin() del ALTER o se
    # auto-bloquea con el lock Sch-M de la transacción abierta.
    for col in columnas:
        enc: str = f"{col}_enc"
        if _columna_existe(engine, enc):
            print(f"     - {enc} ya existe, omito")
            continue
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {TABLA} ADD {enc} VARBINARY(MAX) NULL"))
        print(f"     + {enc} creada")


def f2_backfill(engine: Engine, cipher: AesGcmFieldCipher, columnas: list[str]) -> None:
    print(f"[F2] cifrando {columnas} (backfill)…")
    cols_csv: str = ", ".join(columnas)
    with engine.connect() as conn:
        filas = conn.execute(
            text(f"SELECT numero_documento, {cols_csv} FROM {TABLA}")
        ).all()
    print(f"     {len(filas)} filas a procesar")
    set_clause: str = ", ".join(f"{c}_enc = :{c}" for c in columnas)
    update_sql = text(f"UPDATE {TABLA} SET {set_clause} WHERE numero_documento = :doc")
    lote: list[dict[str, object]] = []
    procesadas: int = 0
    for fila in filas:
        doc = fila[0]
        params: dict[str, object] = {"doc": doc}
        for idx, col in enumerate(columnas, start=1):
            params[col] = cipher.cifrar(
                fila[idx], aad=construir_aad(TABLA, col, str(doc))
            )
        lote.append(params)
        if len(lote) >= BATCH:
            with engine.begin() as conn:
                conn.execute(update_sql, lote)
            procesadas += len(lote)
            print(f"     … {procesadas}/{len(filas)}")
            lote = []
    if lote:
        with engine.begin() as conn:
            conn.execute(update_sql, lote)
        procesadas += len(lote)
    print(f"     backfill completo: {procesadas} filas")


def f3_verify(engine: Engine, cipher: AesGcmFieldCipher, columnas: list[str]) -> bool:
    print("[F3] verificando paridad y descifrado…")
    ok: bool = True
    with engine.connect() as conn:
        for col in columnas:
            plano: int = conn.execute(
                text(f"SELECT COUNT(*) FROM {TABLA} WHERE {col} IS NOT NULL")
            ).scalar_one()
            cifr: int = conn.execute(
                text(f"SELECT COUNT(*) FROM {TABLA} WHERE {col}_enc IS NOT NULL")
            ).scalar_one()
            if plano != cifr:
                ok = False
            estado_col: str = "OK" if plano == cifr else "MISMATCH"
            print(f"     {col}: claro={plano} cifrado={cifr} -> {estado_col}")
            muestra = conn.execute(
                text(
                    f"SELECT TOP 10 numero_documento, {col}, {col}_enc FROM {TABLA} "
                    f"WHERE {col} IS NOT NULL"
                )
            ).all()
            for doc, claro, enc in muestra:
                if cipher.descifrar(enc, aad=construir_aad(TABLA, col, str(doc))) != claro:
                    ok = False
                    print(f"     [X] {col}: descifrado != claro en {doc}")
    print(f"     muestreo de descifrado: {'OK' if ok else 'FALLO'}")
    return ok


def f4_drop(engine: Engine, columnas: list[str]) -> None:
    print("[F4] eliminando columnas en claro (IRREVERSIBLE)…")
    for col in columnas:
        if not _columna_existe(engine, col):
            print(f"     - {col} ya no existe, omito")
            continue
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {TABLA} DROP COLUMN {col}"))
        print(f"     - {col} eliminada")


def cifrar_columnas(columnas: list[str], *, drop: bool) -> None:
    engine: Engine = sync_engine(TARGET_DB, fast_executemany=True)
    cipher: AesGcmFieldCipher = build_cipher()
    print(f"== Cifrado de {columnas} en {TARGET_DB}.{TABLA} ==")
    f0_add(engine, columnas)
    f2_backfill(engine, cipher, columnas)
    if not f3_verify(engine, cipher, columnas):
        raise SystemExit("F3 falló — NO se eliminan columnas en claro. Investigar.")
    if drop:
        f4_drop(engine, columnas)
        print("[OK] Cutover completo: texto plano eliminado; solo queda VARBINARY cifrado.")
    else:
        print("[OK] add+backfill+verify OK. Texto plano conservado. Usa --drop para el cutover.")
