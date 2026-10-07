from __future__ import annotations


class SecretoNoDisponible(Exception):
    """AP-0062: el proveedor de secretos (broker PAM) no pudo entregar un secreto requerido.

    Es una condicion fail-secure: la aplicacion NO cae a un valor local en claro; falla de
    forma controlada para no operar con una credencial no custodiada.
    """
