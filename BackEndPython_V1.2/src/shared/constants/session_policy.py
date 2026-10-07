from __future__ import annotations

from typing import Final

# AP-0162: timeout absoluto de sesion, independiente de la actividad.
JWT_EXPIRE_MINUTES_DEFECTO: Final[int] = 30
# Maximo de politica — staging y produccion no pueden superar 8 horas.
JWT_EXPIRE_MINUTES_MAXIMO: Final[int] = 480

# AP-0129: timeout por INACTIVIDAD (idle), distinto del absoluto de arriba. La sesion se
# cierra tras este tiempo sin actividad del usuario. Canales 7 min, otras apps 20 min.
IDLE_TIMEOUT_CANAL_MIN: Final[int] = 7
IDLE_TIMEOUT_OTRAS_MIN: Final[int] = 20
