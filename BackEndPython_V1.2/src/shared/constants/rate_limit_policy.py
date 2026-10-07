from __future__ import annotations

from typing import Final

# AP-0166: limites de peticiones por IP configurable en .env.
RATE_LIMIT_POR_IP_DEFECTO: Final[str] = "200/minute"
RATE_LIMIT_POR_IP_AUTH: Final[str] = "10/minute"
