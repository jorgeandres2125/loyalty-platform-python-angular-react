"""Medida C (AP-0147 / AP-0095) — cifrado a nivel de aplicación de la cuenta
bancaria en users_perfil_contacto (sufi_db).

Transforma los datos ya cargados en claro a AES-256-GCM, en una secuencia
verificable y con respaldo (sufiatulado queda intacta):

    F0  add     -> añade columnas hermanas numero_de_cuenta_enc / tipo_de_cuenta_enc
    F2  backfill-> cifra los valores existentes en las columnas _enc
    F3  verify  -> paridad de conteos + muestreo de descifrado == texto plano
    F4  drop    -> elimina las columnas en claro (IRREVERSIBLE; exige F3 OK)

Uso:
    .venv/Scripts/python.exe -m migration.cifrar_cuenta_bancaria           # add+backfill+verify
    .venv/Scripts/python.exe -m migration.cifrar_cuenta_bancaria --drop    # + F4 (drop texto plano)

La clave se toma de Settings (APP_ENCRYPTION_KEY de .env.development); no se
hardcodea ni se imprime.
"""
from __future__ import annotations

import base64
import sys
from typing import Final

from sqlalchemy import Engine, text

from migration._common import TARGET_DB, sync_engine
from src.infrastructure.config.settings import Settings
from src.infrastructure.security.aes_gcm_field_cipher import AesGcmFieldCipher
from src.shared.constants.cifrado import TABLA_PERFIL_CONTACTO
from src.shared.utils.cifrado_aad import construir_aad

TABLA: Final[str] = TABLA_PERFIL_CONTACTO
COLUMNAS: Final[tuple[str, ...]] = ("numero_de_cuenta", "tipo_de_cuenta")
BATCH: Final[int] = 1000


def _build_cipher() -> AesGcmFieldCipher:
    settings: Settings = Settings()
    if not settings.app_encryption_key:
        raise SystemExit("APP_ENCRYPTION_KEY no configurada en el entorno — abortando")
    clave: bytes = base64.b64decode(settings.app_encryption_key)
    kid: int = settings.app_encryption_key_id
    return AesGcmFieldCipher({kid: clave}, kid)


def _columna_existe(engine: Engine, columna: str) -> bool:
    sql: str = (
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_NAME = :t AND COLUMN_NAME = :c"
    )
    with engine.connect() as conn:
        total: int = conn.execute(text(sql), {"t": TABLA, "c": columna}).scalar_one()
    return total > 0


def f0_add(engine: Engine) -> None:
    print("[F0] añadiendo columnas _enc VARBINARY(MAX)…")
    # El chequeo de existencia abre su propia conexión; debe hacerse FUERA de la
    # transacción del ALTER. Si no, la consulta de metadatos se auto-bloquea con
    # el lock Sch-M que el ALTER mantiene en la transacción abierta. Cada ALTER va
    # en su propia transacción confirmada.
    for col in COLUMNAS:
        enc: str = f"{col}_enc"
        if _columna_existe(engine, enc):
            print(f"     - {enc} ya existe, omito")
            continue
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {TABLA} ADD {enc} VARBINARY(MAX) NULL"))
        print(f"     + {enc} creada")


def f2_backfill(engine: Engine, cipher: AesGcmFieldCipher) -> None:
    print("[F2] cifrando valores existentes (backfill)…")
    with engine.connect() as conn:
        filas = conn.execute(
            text(f"SELECT numero_documento, numero_de_cuenta, tipo_de_cuenta FROM {TABLA}")
        ).all()
    print(f"     {len(filas)} filas a procesar")
    lote: list[dict[str, object]] = []
    procesadas: int = 0
    update_sql = text(
        f"UPDATE {TABLA} SET numero_de_cuenta_enc = :c, tipo_de_cuenta_enc = :t "
        f"WHERE numero_documento = :doc"
    )
    for doc, cuenta, tipo in filas:
        lote.append({
            "doc": doc,
            "c": cipher.cifrar(cuenta, aad=construir_aad(TABLA, "numero_de_cuenta", str(doc))),
            "t": cipher.cifrar(tipo, aad=construir_aad(TABLA, "tipo_de_cuenta", str(doc))),
        })
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


def f3_verify(engine: Engine, cipher: AesGcmFieldCipher) -> bool:
    print("[F3] verificando paridad y descifrado…")
    ok: bool = True
    with engine.connect() as conn:
        for col in COLUMNAS:
            plano: int = conn.execute(
                text(f"SELECT COUNT(*) FROM {TABLA} WHERE {col} IS NOT NULL")
            ).scalar_one()
            cifr: int = conn.execute(
                text(f"SELECT COUNT(*) FROM {TABLA} WHERE {col}_enc IS NOT NULL")
            ).scalar_one()
            estado: str = "OK" if plano == cifr else "MISMATCH"
            if plano != cifr:
                ok = False
            print(f"     {col}: claro={plano} cifrado={cifr} -> {estado}")

        muestra = conn.execute(
            text(
                f"SELECT TOP 20 numero_documento, numero_de_cuenta, numero_de_cuenta_enc, "
                f"tipo_de_cuenta, tipo_de_cuenta_enc FROM {TABLA} "
                f"WHERE numero_de_cuenta IS NOT NULL OR tipo_de_cuenta IS NOT NULL"
            )
        ).all()
    revisadas: int = 0
    for doc, cuenta, cuenta_enc, tipo, tipo_enc in muestra:
        d_cuenta = cipher.descifrar(
            cuenta_enc, aad=construir_aad(TABLA, "numero_de_cuenta", str(doc))
        )
        d_tipo = cipher.descifrar(tipo_enc, aad=construir_aad(TABLA, "tipo_de_cuenta", str(doc)))
        if d_cuenta != cuenta or d_tipo != tipo:
            ok = False
            print(f"     [X] descifrado != claro en {doc}")
        revisadas += 1
    print(f"     muestreo de descifrado: {revisadas} filas revisadas, {'OK' if ok else 'FALLO'}")
    return ok


def f4_drop(engine: Engine) -> None:
    print("[F4] eliminando columnas en claro (IRREVERSIBLE)…")
    # Mismo patrón que f0_add: el chequeo (conexión aparte) fuera de la transacción
    # del DROP para evitar el auto-bloqueo por el lock Sch-M.
    for col in COLUMNAS:
        if not _columna_existe(engine, col):
            print(f"     - {col} ya no existe, omito")
            continue
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {TABLA} DROP COLUMN {col}"))
        print(f"     - {col} eliminada")


def main() -> None:
    drop: bool = "--drop" in sys.argv
    engine: Engine = sync_engine(TARGET_DB, fast_executemany=True)
    cipher: AesGcmFieldCipher = _build_cipher()
    print(f"== Cifrado de cuenta bancaria en {TARGET_DB}.{TABLA} ==")
    f0_add(engine)
    f2_backfill(engine, cipher)
    if not f3_verify(engine, cipher):
        raise SystemExit("F3 falló — NO se eliminan columnas en claro. Revisar e investigar.")
    if drop:
        f4_drop(engine)
        print("[OK] Cutover completo: el texto plano fue eliminado; solo queda VARBINARY cifrado.")
    else:
        print("[OK] add+backfill+verify OK. Texto plano conservado. Usa --drop para el cutover final.")


if __name__ == "__main__":
    main()
