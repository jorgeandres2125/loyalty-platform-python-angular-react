from __future__ import annotations

import logging
from datetime import UTC, datetime

from src.domain.entities.sesion_activa_entity import SesionActiva
from src.domain.ports.outbound.sesion_repository import SesionRepository
from src.domain.services.politica_sesiones import PoliticaSesiones
from src.domain.value_objects.estado_sesion import EstadoSesion
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD
from src.shared.constants.sesion import EVENTO_SESION_CONCURRENTE

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


def _clave_inicio(sesion: SesionActiva) -> datetime:
    return sesion.inicio


class ServicioSesiones:
    """AP-0130: registra, informa y controla las sesiones concurrentes. AP-0132: al
    cerrarse una sesion (manual o automatica) transiciona su estado con el motivo y la
    fecha de cierre, dejando evidencia auditable del descarte del lado servidor. Modo por
    defecto 'informar' (max 0 = ilimitado). Fail-safe: nunca interrumpe el login."""

    def __init__(
        self, repo: SesionRepository, politica: PoliticaSesiones, habilitado: bool
    ) -> None:
        self._repo: SesionRepository = repo
        self._politica: PoliticaSesiones = politica
        self._habilitado: bool = habilitado

    def _campos(self, resultado: str, uid: int) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_SESION_CONCURRENTE,
            "resultado": resultado,
            "actor": str(uid),
        }

    async def registrar(
        self,
        *,
        sid: str,
        uid: int,
        roles: list[str],
        jti: str,
        device_fp: str,
        ip: str,
        user_agent: str,
        fecha_expiracion: datetime | None = None,
    ) -> None:
        if not self._habilitado or not sid:
            return
        ahora: datetime = datetime.now(UTC)
        maximo: int = self._politica.max_sesiones(roles)
        if maximo > 0:
            activas: list[SesionActiva] = sorted(
                await self._repo.listar_activas(uid), key=_clave_inicio
            )
            sobran: int = len(activas) - (maximo - 1)
            for indice in range(max(0, sobran)):
                await self._repo.cerrar(
                    activas[indice].sid,
                    EstadoSesion.REVOCADA,
                    MotivoCierreSesion.LIMITE_CONCURRENCIA,
                    ahora,
                )
                _logger.info(
                    "AP-0130: sesion previa expulsada por limite de concurrencia",
                    extra=self._campos("expulsion_limite", uid),
                )
        sesion_nueva: SesionActiva = SesionActiva(
            sid=sid,
            uid=uid,
            jti_actual=jti,
            device_fp=device_fp or "",
            ip=ip,
            user_agent=user_agent,
            canal=self._politica.es_canal(roles),
            inicio=ahora,
            last_activity=ahora,
            fecha_expiracion=fecha_expiracion,
        )
        await self._repo.crear(sesion_nueva)
        _logger.info(
            "AP-0130: nueva sesion iniciada", extra=self._campos("nueva_sesion", uid)
        )

    async def listar(self, uid: int) -> list[SesionActiva]:
        # AP-0132: barrido perezoso — antes de informar, marca como expiradas las sesiones
        # cuyo techo de expiracion ya paso (sin scheduler), manteniendo el registro coherente.
        await self.marcar_expiradas(uid)
        return await self._repo.listar_activas(uid)

    async def revocar(self, uid: int, sid: str) -> bool:
        sesion_actual: SesionActiva | None = await self._repo.obtener(sid)
        if sesion_actual is None or sesion_actual.uid != uid:
            return False
        await self._repo.cerrar(
            sid, EstadoSesion.REVOCADA, MotivoCierreSesion.LOGOUT, datetime.now(UTC)
        )
        _logger.info(
            "AP-0130: sesion revocada por el usuario",
            extra=self._campos("revocada_usuario", uid),
        )
        return True

    async def revocar_otras(self, uid: int, sid_actual: str) -> int:
        activas: list[SesionActiva] = await self._repo.listar_activas(uid)
        ahora: datetime = datetime.now(UTC)
        revocadas: int = 0
        for sesion_item in activas:
            if sesion_item.sid != sid_actual:
                await self._repo.cerrar(
                    sesion_item.sid,
                    EstadoSesion.REVOCADA,
                    MotivoCierreSesion.LOGOUT,
                    ahora,
                )
                revocadas += 1
        if revocadas:
            _logger.info(
                "AP-0130: cierre de las demas sesiones del usuario",
                extra=self._campos("revocada_otras", uid),
            )
        return revocadas

    async def cerrar(self, sid: str, motivo: MotivoCierreSesion) -> None:
        # AP-0132: cierra una sesion concreta por su sid con un motivo (logout, cambio de
        # credencial, etc.). Idempotente y fail-safe; complementa la revocacion del jti
        # (AP-0021) marcando tambien la sesion en el registro para dejar evidencia.
        if not self._habilitado or not sid:
            return
        await self._repo.cerrar(
            sid, EstadoSesion.REVOCADA, motivo, datetime.now(UTC)
        )
        _logger.info(
            "AP-0132: sesion cerrada",
            extra={
                "evento_seguridad": EVENTO_SESION_CONCURRENTE,
                "resultado": motivo.value,
                "actor": "",
            },
        )

    async def cerrar_todas(self, uid: int, motivo: MotivoCierreSesion) -> int:
        # AP-0132: cierra todas las sesiones activas del usuario (logout global, revocacion
        # administrativa, cambio de credencial). Complementa la revocacion masiva por
        # token_version (AP-0049) dejando evidencia por sesion en el registro.
        if not self._habilitado:
            return 0
        activas: list[SesionActiva] = await self._repo.listar_activas(uid)
        ahora: datetime = datetime.now(UTC)
        cerradas: int = 0
        for sesion_item in activas:
            await self._repo.cerrar(
                sesion_item.sid, EstadoSesion.REVOCADA, motivo, ahora
            )
            cerradas += 1
        if cerradas:
            _logger.info(
                "AP-0132: cierre de todas las sesiones del usuario",
                extra=self._campos("cerrar_todas", uid),
            )
        return cerradas

    async def marcar_expiradas(self, uid: int) -> int:
        # AP-0132: transicion perezosa ACTIVA -> EXPIRADA para las sesiones cuyo techo de
        # expiracion ya paso. El enforcement lo garantiza require_token (el JWT vencido es
        # rechazado); esto mantiene el registro coherente y deja evidencia de auditoria.
        if not self._habilitado:
            return 0
        ahora: datetime = datetime.now(UTC)
        expiradas: int = 0
        for sesion_item in await self._repo.listar_activas(uid):
            venc: datetime | None = sesion_item.fecha_expiracion
            if venc is not None and venc <= ahora:
                await self._repo.cerrar(
                    sesion_item.sid,
                    EstadoSesion.EXPIRADA,
                    MotivoCierreSesion.EXPIRACION,
                    venc,
                )
                expiradas += 1
        return expiradas

    async def esta_revocada(self, sid: str) -> bool:
        return await self._repo.esta_revocada(sid)

    async def tocar_actividad(self, sid: str) -> None:
        # AP-0130 y AP-0129: registra la ultima actividad de la sesion (se invoca desde el
        # endpoint de renovacion, no en cada peticion, para no sumar latencia por request).
        if not self._habilitado or not sid:
            return
        await self._repo.actualizar_actividad(sid, datetime.now(UTC))
