from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.value_objects.permiso import Permiso


@dataclass(frozen=True)
class ReglaAcceso:
    """AP-0055: regla declarativa de acceso para un par (tipo de recurso, accion).

    permisos: cualquiera de estos permite la accion (vacio = cualquier autenticado).
    staff_bypass: permisos de gestion sobre terceros que omiten la verificacion de
    propiedad. ownership_required: exige que el actor sea dueno del objeto (salvo
    staff). deny_status: codigo HTTP al denegar por propiedad (403, o 404 para ocultar
    la existencia de objetos enumerables sensibles).
    """

    permisos: frozenset[Permiso] = field(default_factory=frozenset)
    staff_bypass: frozenset[Permiso] = field(default_factory=frozenset)
    ownership_required: bool = False
    deny_status: int = 403
