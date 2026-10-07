from __future__ import annotations

from typing import Final

# AP-0180: proveedores de custodia de la clave maestra (KEK).
KMS_PROVIDER_LOCAL: Final[str] = "local"
KMS_PROVIDER_AWS: Final[str] = "aws"

# Proveedores que respaldan el KEK en un HSM o KMS sin exponerlo al proceso.
KMS_PROVIDERS_RESPALDADOS_HSM: Final[frozenset[str]] = frozenset({KMS_PROVIDER_AWS})

# Valores aceptados por la configuracion KMS_PROVIDER.
KMS_PROVIDERS_VALIDOS: Final[frozenset[str]] = frozenset(
    {KMS_PROVIDER_LOCAL, KMS_PROVIDER_AWS}
)
