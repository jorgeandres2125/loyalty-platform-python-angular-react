from __future__ import annotations

from typing import Final

# Politica de ciclo de vida de contrasenas.
#
# AP-0037: aviso de vencimiento con 7 dias de antelacion.
# AP-0038: cambio autonomo hasta N dias despues del vencimiento (gracia).
# AP-0042: vigencia maxima de 45 dias (se baja el defecto historico de 90 a 45).
# AP-0041: no reutilizar las ultimas N contrasenas (defecto 24).
# AP-0043: un solo cambio de contrasena por dia (zona horaria de negocio).
#
# El aviso NO bloquea el acceso (AP-0037); el enforcement de vencimiento (AP-0038 y
# AP-0042) es conmutable por entorno para un despliegue gradual.
PASSWORD_VIGENCIA_DIAS_DEFECTO: Final[int] = 45

PASSWORD_AVISO_DIAS_DEFECTO: Final[int] = 7

PASSWORD_GRACIA_DIAS_DEFECTO: Final[int] = 5

PASSWORD_HISTORIAL_TAMANO_DEFECTO: Final[int] = 24

PASSWORD_TIMEZONE_DEFECTO: Final[str] = "America/Bogota"
