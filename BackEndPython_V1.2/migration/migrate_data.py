"""Copia los datos usados desde sufiatulado -> sufi_db respetando los FKs nuevos.

Estrategia (acordada con el cliente):
  - Orden de dependencias (padres primero) para satisfacer los FKs.
  - FK opcional huérfano  -> se pone NULL (la fila se conserva).
  - Fila hija sin padre obligatorio (PK/columna NOT NULL) -> se OMITE.
  - numero_documento se castea a nvarchar(40) (ADR-02); user_documento viene
    de numeric en el origen.
  - IDENTITY_INSERT ON en tablas con PK autoincremental para preservar los IDs.
  - Idempotente: borra el destino (orden inverso) antes de cargar.

Las columnas se intersectan por nombre entre origen y destino en tiempo de
ejecución, así que columnas SSMA extra del origen (p.ej. __pk) se ignoran solas.

Uso:
    .venv/Scripts/python.exe -m migration.migrate_data
"""
from __future__ import annotations

from typing import Any, Final

from migration._common import SOURCE_DB, TARGET_DB, sync_engine

# (columna_hija, tabla_padre, columna_padre, accion)  accion = "null" | "skip"
OrphanRule = tuple[str, str, str, str]


class TablePlan:
    def __init__(
        self,
        name: str,
        *,
        orphans: list[OrphanRule] | None = None,
        casts: dict[str, str] | None = None,
    ) -> None:
        self.name: str = name
        self.orphans: list[OrphanRule] = orphans or []
        self.casts: dict[str, str] = casts or {}


# Orden de carga (padres antes que hijos).
PLAN: Final[list[TablePlan]] = [
    TablePlan("departamentos"),
    TablePlan("ciudades", orphans=[("did", "departamentos", "did", "skip")]),
    TablePlan("afp"),
    TablePlan("arl"),
    TablePlan("eps"),
    TablePlan("bancos"),
    TablePlan("taxonomia_profesion"),
    TablePlan("role"),
    TablePlan("users"),
    TablePlan(
        "users_roles",
        orphans=[
            ("uid", "users", "uid", "skip"),
            ("rid", "role", "rid", "skip"),
        ],
    ),
    TablePlan("canales"),
    TablePlan("oficinas"),
    TablePlan(
        "canales_oficinas",
        orphans=[
            ("cod_canales", "canales", "cod_canales", "null"),
            ("cod_oficinas", "oficinas", "cod_oficinas", "null"),
        ],
    ),
    TablePlan("comisionistas_programa"),
    TablePlan(
        "comisionistas_subprograma",
        orphans=[("cpid", "comisionistas_programa", "cpid", "null")],
    ),
    TablePlan("frontend_modules"),
    TablePlan(
        "frontend_modules_permissions",
        orphans=[
            ("rid", "role", "rid", "skip"),
            ("module_id", "frontend_modules", "module_id", "skip"),
        ],
    ),
    TablePlan(
        "users_perfil_contacto",
        orphans=[
            ("banco", "bancos", "tid", "null"),
            ("cod_canales", "canales", "cod_canales", "null"),
            ("cod_oficinas", "oficinas", "cod_oficinas", "null"),
            ("comisionista_programa_id", "comisionistas_programa", "cpid", "null"),
            ("comisionista_subprograma_id", "comisionistas_subprograma", "cspid", "null"),
            ("usuario_responsable", "users", "uid", "null"),
        ],
        casts={"numero_documento": "CAST(s.[numero_documento] AS nvarchar(40))"},
    ),
    TablePlan(
        "users_perfil_tributario",
        orphans=[
            ("numero_documento", "users_perfil_contacto", "numero_documento", "skip"),
            ("eps", "eps", "tid", "null"),
            ("afp", "afp", "tid", "null"),
            ("arl", "arl", "tid", "null"),
        ],
        casts={"numero_documento": "CAST(s.[numero_documento] AS nvarchar(40))"},
    ),
    TablePlan(
        "users_perfil_emocional",
        orphans=[("numero_documento", "users_perfil_contacto", "numero_documento", "skip")],
        casts={"numero_documento": "CAST(s.[numero_documento] AS nvarchar(40))"},
    ),
    TablePlan(
        "user_documento",
        orphans=[("numero_documento", "users_perfil_contacto", "numero_documento", "null")],
        casts={"numero_documento": "CAST(s.[numero_documento] AS nvarchar(40))"},
    ),
    TablePlan("Ejecutivos"),
    TablePlan("users_ejecutivos"),
]


def _columns(cursor: Any, db: str, table: str) -> list[str]:
    cursor.execute(
        f"SELECT COLUMN_NAME FROM {db}.INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_NAME = ? ORDER BY ORDINAL_POSITION",
        table,
    )
    return [row[0] for row in cursor.fetchall()]


def _identity_col(cursor: Any, table: str) -> str | None:
    cursor.execute(
        f"SELECT c.name FROM {TARGET_DB}.sys.columns c "
        f"JOIN {TARGET_DB}.sys.objects o ON o.object_id = c.object_id "
        "WHERE o.name = ? AND c.is_identity = 1",
        table,
    )
    row = cursor.fetchone()
    return str(row[0]) if row else None


def _count(cursor: Any, db: str, table: str) -> int:
    cursor.execute(f"SELECT COUNT(*) FROM {db}.dbo.[{table}]")
    return int(cursor.fetchone()[0])


_CHAR_TYPES: Final[frozenset[str]] = frozenset(
    {"char", "nchar", "varchar", "nvarchar", "text", "ntext"}
)


def _char_columns(cursor: Any, table: str) -> set[str]:
    """Columnas de tipo carácter en el ORIGEN (para decidir COLLATE)."""
    cursor.execute(
        f"SELECT COLUMN_NAME FROM {SOURCE_DB}.INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_NAME = ? AND DATA_TYPE IN "
        "('char','nchar','varchar','nvarchar','text','ntext')",
        table,
    )
    return {row[0] for row in cursor.fetchall()}


def _col_expr(plan: TablePlan, col: str) -> str:
    """Expresión SELECT para una columna: cast si aplica, si no s.[col]."""
    return plan.casts.get(col, f"s.[{col}]")


def _cmp_expr(plan: TablePlan, col: str, char_cols: set[str]) -> str:
    """Expresión del lado ORIGEN para comparar contra el padre (destino).

    Las collations de origen y destino difieren; en columnas de texto se fuerza
    COLLATE DATABASE_DEFAULT para evitar el conflicto. En int sería error, por eso
    solo se aplica a columnas carácter (o con cast a nvarchar).
    """
    base: str = _col_expr(plan, col)
    if col in char_cols or col in plan.casts:
        return f"({base}) COLLATE DATABASE_DEFAULT"
    return base


def main() -> None:
    engine = sync_engine(TARGET_DB)
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()

        # 1) Limpiar destino en orden inverso (idempotencia).
        print("Limpiando destino (orden inverso) ...")
        for plan in reversed(PLAN):
            cur.execute(f"DELETE FROM {TARGET_DB}.dbo.[{plan.name}]")
        raw.commit()

        # 2) Cargar tabla por tabla.
        report: list[str] = []
        for plan in PLAN:
            src_cols: list[str] = _columns(cur, SOURCE_DB, plan.name)
            tgt_cols: list[str] = _columns(cur, TARGET_DB, plan.name)
            common: list[str] = [c for c in tgt_cols if c in src_cols]
            char_cols: set[str] = _char_columns(cur, plan.name)

            # Para columnas con cast (origen de tipo distinto) las incluimos aunque
            # el nombre exista; ya están en common por nombre.
            null_rules: dict[str, OrphanRule] = {
                r[0]: r for r in plan.orphans if r[3] == "null"
            }
            skip_rules: list[OrphanRule] = [r for r in plan.orphans if r[3] == "skip"]

            select_parts: list[str] = []
            for col in common:
                base: str = _col_expr(plan, col)
                if col in null_rules:
                    _, pt, pc, _ = null_rules[col]
                    cmp: str = _cmp_expr(plan, col, char_cols)
                    expr: str = (
                        f"CASE WHEN {base} IS NOT NULL AND EXISTS "
                        f"(SELECT 1 FROM {TARGET_DB}.dbo.[{pt}] p WHERE p.[{pc}] = {cmp}) "
                        f"THEN {base} ELSE NULL END"
                    )
                    select_parts.append(f"{expr} AS [{col}]")
                else:
                    select_parts.append(f"{base} AS [{col}]")

            where_parts: list[str] = []
            for child_col, pt, pc, _ in skip_rules:
                cexpr: str = _cmp_expr(plan, child_col, char_cols)
                where_parts.append(
                    f"EXISTS (SELECT 1 FROM {TARGET_DB}.dbo.[{pt}] p WHERE p.[{pc}] = {cexpr})"
                )
            where_sql: str = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""

            col_list: str = ", ".join(f"[{c}]" for c in common)
            select_sql: str = ", ".join(select_parts)
            insert_sql: str = (
                f"INSERT INTO {TARGET_DB}.dbo.[{plan.name}] ({col_list}) "
                f"SELECT {select_sql} FROM {SOURCE_DB}.dbo.[{plan.name}] s{where_sql}"
            )

            # IDENTITY_INSERT solo si la columna identidad viene en el origen
            # (si es un PK surrogado nuevo, p.ej. Ejecutivos.id, se autogenera).
            ident: str | None = _identity_col(cur, plan.name)
            use_identity: bool = ident is not None and ident in common
            if use_identity:
                cur.execute(f"SET IDENTITY_INSERT {TARGET_DB}.dbo.[{plan.name}] ON")
            cur.execute(insert_sql)
            inserted: int = cur.rowcount
            if use_identity:
                cur.execute(f"SET IDENTITY_INSERT {TARGET_DB}.dbo.[{plan.name}] OFF")
            raw.commit()

            src_total: int = _count(cur, SOURCE_DB, plan.name)
            skipped: int = src_total - inserted
            flag: str = "" if skipped == 0 else f"  (OMITIDAS: {skipped})"
            line: str = f"{plan.name:<32} origen={src_total:>6}  insertadas={inserted:>6}{flag}"
            print(line)
            report.append(line)

        print("\n=== RESUMEN ===")
        for line in report:
            print(line)
    finally:
        raw.close()
        engine.dispose()


if __name__ == "__main__":
    main()
