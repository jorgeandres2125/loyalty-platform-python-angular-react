from __future__ import annotations

from enum import StrEnum


class EstadoCredencial(StrEnum):
    """AP-0038: estado de la contrasena respecto de su vencimiento y ventana de gracia.

    - VIGENTE: contrasena valida (aun no vence).
    - EN_GRACIA: vencida pero dentro de los dias de gracia; se permite el cambio
      autonomo (el usuario aun conoce su contrasena vencida).
    - FUERA_GRACIA: vencida hace mas dias que la gracia; el cambio autonomo por el
      flujo estandar queda bloqueado (requiere restablecimiento asistido).
    """

    VIGENTE = "vigente"
    EN_GRACIA = "en_gracia"
    FUERA_GRACIA = "fuera_gracia"
