from __future__ import annotations


class AudienciaNoPermitida(Exception):
    """AP-0146: la aplicacion de terceros (audience) no esta autorizada."""

    def __init__(self, audiencia: str) -> None:
        super().__init__(
            f"La aplicacion '{audiencia}' no esta autorizada para emitir tokens."
        )
        self.audiencia: str = audiencia
