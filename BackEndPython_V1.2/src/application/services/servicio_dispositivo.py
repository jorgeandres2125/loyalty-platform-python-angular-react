from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime

from src.application.dto.resultado_dispositivo_dto import ResultadoDispositivoDTO
from src.domain.entities.dispositivo_usuario import DispositivoUsuario
from src.domain.ports.outbound.dispositivo_repository import DispositivoRepository
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.shared.constants.dispositivo import EVENTO_DISPOSITIVO, USER_AGENT_MAX
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)

_NAVEGADORES: tuple[tuple[str, str], ...] = (
    ("Edg", "Edge"),
    ("OPR", "Opera"),
    ("Chrome", "Chrome"),
    ("Firefox", "Firefox"),
    ("Safari", "Safari"),
)
_SISTEMAS: tuple[tuple[str, str], ...] = (
    ("Windows NT 10", "Windows 10 u 11"),
    ("Windows", "Windows"),
    ("Android", "Android"),
    ("iPhone", "iOS"),
    ("iPad", "iOS"),
    ("Mac OS", "macOS"),
    ("Linux", "Linux"),
)


class ServicioDispositivo:
    """AP-0014: identifica y registra el equipo origen de cada autenticacion.

    Calcula una huella normalizada del equipo (del fingerprint que envia el navegador o,
    en su defecto, del User-Agent), reconoce los equipos ya vistos por el usuario y
    registra los nuevos; audita cada acceso (AP-0022) y emite una alerta de seguridad de
    severidad alta cuando el equipo es desconocido para ese usuario. Deshabilitado, es
    no-op.
    """

    def __init__(self, repo: DispositivoRepository, enabled: bool) -> None:
        self._repo: DispositivoRepository = repo
        self._enabled: bool = enabled

    async def registrar_acceso_async(
        self,
        uid: int,
        fingerprint: str | None,
        device_name: str | None,
        user_agent: str,
        ip: str,
    ) -> ResultadoDispositivoDTO:
        if not self._enabled:
            return ResultadoDispositivoDTO(device_hash="", es_nuevo=False, device_name="")
        ua: str = (user_agent or "")[:USER_AGENT_MAX]
        base: str = (fingerprint or ua or "desconocido").strip()
        device_hash: str = hashlib.sha256(base.encode("utf-8")).hexdigest()
        nombre: str = (device_name or self._nombre_desde(ua) or "Equipo desconocido")[:200]
        ahora: str = datetime.now(UTC).isoformat()
        existente: DispositivoUsuario | None = await self._repo.obtener(uid, device_hash)
        if existente is not None:
            await self._repo.guardar(existente.con_acceso(ahora))
            _logger.info(
                "AP-0014 acceso desde dispositivo conocido uid=%s",
                uid,
                extra=self._campos("exito", SeveridadSeguridad.INFORMATIVA, uid, "conocido", ip),
            )
            return ResultadoDispositivoDTO(
                device_hash=device_hash, es_nuevo=False, device_name=existente.device_name
            )
        nuevo: DispositivoUsuario = DispositivoUsuario(
            uid=uid,
            device_hash=device_hash,
            device_name=nombre,
            user_agent=ua,
            first_login_iso=ahora,
            last_login_iso=ahora,
            veces_visto=1,
            trusted=False,
        )
        await self._repo.guardar(nuevo)
        _logger.warning(
            "AP-0014 acceso desde dispositivo NUEVO uid=%s ip=%s nombre=%s",
            uid,
            ip,
            nombre,
            extra=self._campos("nuevo", SeveridadSeguridad.ALTA, uid, "nuevo", ip),
        )
        return ResultadoDispositivoDTO(
            device_hash=device_hash, es_nuevo=True, device_name=nombre
        )

    async def listar_por_usuario_async(self, uid: int) -> list[DispositivoUsuario]:
        return await self._repo.listar_por_usuario(uid)

    @staticmethod
    def _nombre_desde(user_agent: str) -> str:
        navegador: str = next(
            (nombre for clave, nombre in _NAVEGADORES if clave in user_agent), ""
        )
        sistema: str = next(
            (nombre for clave, nombre in _SISTEMAS if clave in user_agent), ""
        )
        if navegador and sistema:
            return navegador + " en " + sistema
        return navegador or sistema or ""

    @staticmethod
    def _campos(
        resultado: str, severidad: SeveridadSeguridad, uid: int, detalle: str, ip: str
    ) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_DISPOSITIVO,
            "resultado": resultado,
            "severidad": severidad.value,
            "actor": str(uid),
            "detalle": detalle,
            "ip": ip,
        }
