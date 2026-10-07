from __future__ import annotations

from src.domain.ports.outbound.notificador_correo import NotificadorCorreo


class EnviarCorreoMasivoUseCase:
    """AP-0088 -- Punto de entrada unico para el envio MASIVO de correo.

    Normaliza y deduplica la lista de destinatarios y delega en
    NotificadorCorreo.enviar_masivo_async, cuyo contrato garantiza que los
    destinatarios viajan ocultos entre si (BCC o CCO). Cualquier funcionalidad
    futura de correo masivo debe pasar por aqui, nunca por envios individuales
    en bucle que expongan la lista de destinatarios.
    """

    def __init__(self, notificador: NotificadorCorreo) -> None:
        self._notificador: NotificadorCorreo = notificador

    async def ejecutar_async(
        self,
        destinatarios: list[str],
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> int:
        limpios: list[str] = self._normalizar(destinatarios)
        if not limpios:
            return 0
        await self._notificador.enviar_masivo_async(
            destinatarios=limpios,
            asunto=asunto,
            cuerpo_texto=cuerpo_texto,
            cuerpo_html=cuerpo_html,
        )
        return len(limpios)

    @staticmethod
    def _normalizar(destinatarios: list[str]) -> list[str]:
        vistos: set[str] = set()
        limpios: list[str] = []
        for crudo in destinatarios:
            correo: str = crudo.strip()
            clave: str = correo.lower()
            if correo and clave not in vistos:
                vistos.add(clave)
                limpios.append(correo)
        return limpios
