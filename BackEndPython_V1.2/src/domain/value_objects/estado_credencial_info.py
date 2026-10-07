from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.estado_credencial import EstadoCredencial


@dataclass(frozen=True)
class EstadoCredencialInfo:
    """AP-0038: resultado de clasificar el estado de vencimiento de una contrasena.

    Ademas del estado lleva los dias transcurridos desde el vencimiento y los dias
    de gracia que restan para el cambio autonomo, de modo que la capa HTTP arme las
    respuestas (409 en gracia, 403 fuera de gracia) sin recalcular.
    """

    estado: EstadoCredencial
    dias_desde_vencimiento: int
    dias_restantes_gracia: int
