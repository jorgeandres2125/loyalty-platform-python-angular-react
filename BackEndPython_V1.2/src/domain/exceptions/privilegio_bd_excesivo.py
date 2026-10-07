from __future__ import annotations


class PrivilegioBdExcesivo(Exception):
    """AP-0056: el principal de BD conectado pertenece a roles privilegiados (sysadmin,
    db_owner, db_securityadmin, db_accessadmin o db_ddladmin), violando el principio de
    minimo privilegio. En staging y produccion aborta el arranque (fail-fast).
    """
