from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime

from src.domain.entities.password_temporal_entity import PasswordTemporalEntity
from src.domain.exceptions.password_temporal_requiere_cambio import (
    PasswordTemporalRequiereCambio,
)
from src.domain.exceptions.password_temporal_vencida import PasswordTemporalVencida
from src.domain.ports.outbound.password_temporal_repository import (
    PasswordTemporalRepository,
)
from src.domain.ports.outbound.usuario_repository import UsuarioRepository
from src.domain.services.politica_password_temporal import PoliticaPasswordTemporal
from src.domain.value_objects.estado_password_temporal import EstadoPasswordTemporal
from src.domain.value_objects.origen_password_temporal import OrigenPasswordTemporal
from src.infrastructure.security.password_hasher import PasswordHasher
from src.shared.constants.password_temporal import (
    PASSWORD_TEMPORAL_DIGITOS,
    PASSWORD_TEMPORAL_LONGITUD_DEFECTO,
    PASSWORD_TEMPORAL_MAYUSCULAS,
    PASSWORD_TEMPORAL_MINUSCULAS,
)

_logger: logging.Logger = logging.getLogger("sufi.password_temporal")


class ServicioPasswordTemporal:
    """AP-0046, AP-0047 y AP-0048: orquesta el ciclo de vida de la credencial temporal.

    - emitir: genera la clave (CSPRNG, alfabeto legible, 3 clases garantizadas),
      la hashea con bcrypt, invalida la vigente previa (REEMPLAZADA) y persiste el
      origen completo (quien, desde donde, por que) para AP-0047.
    - verificar_login: rama del login que se ejecuta SOLO tras fallar la credencial
      permanente. Con match de la temporal vigente estampa el primer uso (AP-0046)
      y lanza PasswordTemporalRequiereCambio; vencida (AP-0048) lanza
      PasswordTemporalVencida; en cualquier otro caso no interfiere.
    - validar_para_cambio y consumir: soporte del endpoint de cambio obligatorio.

    Fail-safe: si la tabla no existe (migracion pendiente) o la lectura falla, la
    rama temporal se desactiva con un warning y el login normal queda intacto.
    """

    def __init__(
        self,
        repo: PasswordTemporalRepository,
        politica: PoliticaPasswordTemporal,
        hasher: PasswordHasher,
        habilitado: bool = True,
        longitud: int = PASSWORD_TEMPORAL_LONGITUD_DEFECTO,
    ) -> None:
        self._repo: PasswordTemporalRepository = repo
        self._politica: PoliticaPasswordTemporal = politica
        self._hasher: PasswordHasher = hasher
        self._habilitado: bool = habilitado
        self._longitud: int = longitud

    @staticmethod
    def _ahora(ahora: datetime | None) -> datetime:
        return ahora if ahora is not None else datetime.now(UTC).replace(tzinfo=None)

    def generar_clave(self) -> str:
        # CSPRNG con las tres clases garantizadas (dos caracteres de cada una) y el
        # resto uniforme sobre el alfabeto completo; mezcla tambien criptografica.
        alfabeto: str = (
            PASSWORD_TEMPORAL_MINUSCULAS
            + PASSWORD_TEMPORAL_MAYUSCULAS
            + PASSWORD_TEMPORAL_DIGITOS
        )
        caracteres: list[str] = []
        for clase in (
            PASSWORD_TEMPORAL_MINUSCULAS,
            PASSWORD_TEMPORAL_MAYUSCULAS,
            PASSWORD_TEMPORAL_DIGITOS,
        ):
            caracteres.append(secrets.choice(clase))
            caracteres.append(secrets.choice(clase))
        while len(caracteres) < self._longitud:
            caracteres.append(secrets.choice(alfabeto))
        secrets.SystemRandom().shuffle(caracteres)
        return "".join(caracteres)

    async def emitir(
        self,
        uid: int,
        emitida_por_uid: int,
        emitida_por_usuario: str,
        origen: OrigenPasswordTemporal,
        motivo: str | None = None,
        ip_emision: str | None = None,
        ahora: datetime | None = None,
    ) -> tuple[PasswordTemporalEntity, str]:
        instante: datetime = self._ahora(ahora)
        clave: str = self.generar_clave()
        entidad: PasswordTemporalEntity = PasswordTemporalEntity(
            uid=uid,
            hash_temporal=self._hasher.hashear(clave),
            emitida_por_uid=emitida_por_uid,
            emitida_por_usuario=emitida_por_usuario,
            origen=origen,
            emitida_iso=instante.isoformat(),
            expira_iso=self._politica.calcular_expiracion(instante).isoformat(),
            estado=EstadoPasswordTemporal.ACTIVA,
            motivo=motivo,
            ip_emision=ip_emision,
        )
        creada: PasswordTemporalEntity = await self._repo.crear(entidad)
        return creada, clave

    async def verificar_login(
        self,
        username: str,
        password: str,
        usuario_repo: UsuarioRepository,
        ahora: datetime | None = None,
    ) -> None:
        if not self._habilitado:
            return
        try:
            usuario = await usuario_repo.obtener_por_nombre_async(username)
            if usuario is None:
                return
            uid: int = usuario.uid or 0
            entidad: PasswordTemporalEntity | None = await self._repo.obtener_vigente(uid)
        except Exception as exc:  # noqa: BLE001 -- fail-safe: no rompe el login normal
            _logger.warning(
                "AP-0046: rama temporal deshabilitada por error de lectura: %s", exc
            )
            return
        if entidad is None:
            return
        if not self._hasher.verificar(password, entidad.hash_temporal):
            return
        instante: datetime = self._ahora(ahora)
        if not self._politica.puede_autenticar(entidad, instante):
            # AP-0048: match exacto pero fuera de la vigencia (o estado no vigente,
            # guarda adicional al filtro del repositorio).
            raise PasswordTemporalVencida(entidad.expira_iso)
        if entidad.usada_iso is None and entidad.id is not None:
            # AP-0046: primer uso -> queda estampado; desde ahora solo vale para
            # el cambio obligatorio (nunca emite sesion plena).
            await self._repo.marcar_usada(entidad.id, instante.isoformat())
        raise PasswordTemporalRequiereCambio(entidad.expira_iso)

    async def validar_para_cambio(
        self, uid: int, password: str, ahora: datetime | None = None
    ) -> PasswordTemporalEntity | None:
        # Devuelve la temporal SOLO si coincide y puede autenticar; vencida con
        # match lanza PasswordTemporalVencida; sin match devuelve None (generico).
        if not self._habilitado:
            return None
        try:
            entidad: PasswordTemporalEntity | None = await self._repo.obtener_vigente(uid)
        except Exception as exc:  # noqa: BLE001 -- fail-safe
            _logger.warning("AP-0046: no se pudo leer la temporal uid=%s: %s", uid, exc)
            return None
        if entidad is None:
            return None
        if not self._hasher.verificar(password, entidad.hash_temporal):
            return None
        if not self._politica.puede_autenticar(entidad, self._ahora(ahora)):
            raise PasswordTemporalVencida(entidad.expira_iso)
        return entidad

    def coincide(self, entidad: PasswordTemporalEntity, password: str) -> bool:
        return self._hasher.verificar(password, entidad.hash_temporal)

    async def consumir(
        self, entidad: PasswordTemporalEntity, ahora: datetime | None = None
    ) -> None:
        if entidad.id is not None:
            await self._repo.marcar_consumida(
                entidad.id, self._ahora(ahora).isoformat()
            )
