from __future__ import annotations

from src.application.services.servicio_password_temporal import ServicioPasswordTemporal
from src.application.services.servicio_sesiones import ServicioSesiones
from src.domain.entities.password_temporal_entity import PasswordTemporalEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.ports.outbound.estado_credencial_repository import EstadoCredencialRepository
from src.domain.ports.outbound.usuario_repository import UsuarioRepository
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion
from src.domain.value_objects.origen_password_temporal import OrigenPasswordTemporal


class EmitirPasswordTemporalUseCase:
    """AP-0047: emision de una contrasena temporal por un tercero autorizado.

    Verifica que el usuario destino exista (incluye cuentas deshabilitadas: el
    restablecimiento suele preceder a la reactivacion) y delega en el servicio la
    generacion, el reemplazo de la vigente previa y la persistencia del origen.
    La clave en claro solo viaja en la respuesta de esta operacion (una vez).
    AP-0049: emitirla revoca de inmediato las sesiones vivas del usuario destino
    (token_version++), como todo restablecimiento de credencial por un tercero.
    """

    def __init__(
        self,
        servicio: ServicioPasswordTemporal,
        usuario_repo: UsuarioRepository,
        estado_credencial: EstadoCredencialRepository | None = None,
        sesiones: ServicioSesiones | None = None,
    ) -> None:
        self._servicio: ServicioPasswordTemporal = servicio
        self._usuario_repo: UsuarioRepository = usuario_repo
        self._estado_credencial: EstadoCredencialRepository | None = estado_credencial
        self._sesiones: ServicioSesiones | None = sesiones

    async def ejecutar_async(
        self,
        uid_objetivo: int,
        emitida_por_uid: int,
        emitida_por_usuario: str,
        origen: OrigenPasswordTemporal,
        motivo: str | None,
        ip_emision: str | None,
    ) -> tuple[PasswordTemporalEntity, str, UsuarioEntity]:
        usuario: UsuarioEntity | None = (
            await self._usuario_repo.obtener_cualquiera_por_uid_async(uid_objetivo)
        )
        if usuario is None:
            raise LookupError("Usuario no encontrado")
        entidad, clave = await self._servicio.emitir(
            uid=uid_objetivo,
            emitida_por_uid=emitida_por_uid,
            emitida_por_usuario=emitida_por_usuario,
            origen=origen,
            motivo=motivo,
            ip_emision=ip_emision,
        )
        if self._estado_credencial is not None:
            # AP-0049: el restablecimiento por un tercero invalida en el acto
            # todas las sesiones vivas del usuario destino.
            await self._estado_credencial.incrementar_version(uid_objetivo)
        # AP-0208: cierra tambien las sesiones en el registro (evidencia por sesion).
        if self._sesiones is not None:
            await self._sesiones.cerrar_todas(
                uid_objetivo, MotivoCierreSesion.CAMBIO_CREDENCIAL
            )
        return entidad, clave, usuario
