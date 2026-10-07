from __future__ import annotations

import asyncio
import logging
import secrets
import time
from collections.abc import Sequence
from datetime import UTC, datetime

from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.credenciales_invalidas import CredencialesInvalidas
from src.domain.exceptions.password_insegura import PasswordInsegura
from src.domain.exceptions.password_reutilizada import PasswordReutilizada
from src.domain.ports.outbound.password_history_repository import (
    PasswordHistoryRepository,
)
from src.domain.ports.outbound.usuario_repository import UsuarioRepository
from src.domain.services.crypto_sapin import CryptoSAPIN
from src.domain.services.politica_inactividad import PoliticaInactividad
from src.domain.services.validador_password import ValidadorPassword
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import PasswordHasher
from src.shared.constants.password_expiracion import PASSWORD_HISTORIAL_TAMANO_DEFECTO

logger: logging.Logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        jwt_handler: JWTHandler,
        password_hasher: PasswordHasher,
        jwt_expire_minutes: int,
        crypto_sapin: CryptoSAPIN | None = None,
        politica_inactividad: PoliticaInactividad | None = None,
    ) -> None:
        self._jwt: JWTHandler = jwt_handler
        self._hasher: PasswordHasher = password_hasher
        self._jwt_expire_minutes: int = jwt_expire_minutes
        self._crypto: CryptoSAPIN | None = crypto_sapin
        self._politica: PoliticaInactividad | None = politica_inactividad

    # -- Token ----------------------------------------------------------------

    def generar_token(
        self, usuario: UsuarioEntity, token_version: int = 1, amr: list[str] | None = None
    ) -> str:
        ahora: int = int(time.time())
        roles: list[str] = [rol.value for rol in usuario.roles]
        payload: dict[str, object] = {
            "sub": str(usuario.uid),
            "nombre": usuario.nombre,
            "roles": roles,
            "jti": secrets.token_urlsafe(16),
            # AP-0130: identificador de sesion, estable entre renovaciones (a diferencia
            # del jti, que rota en cada refresh). Lo usa el Session Registry.
            "sid": secrets.token_urlsafe(16),
            "tv": token_version,
            "auth_epoch": ahora,
            "amr": amr if amr is not None else ["pwd"],
        }
        # AP-0129: si hay politica de inactividad, el TTL del token es el limite de
        # inactividad (canal 7 min, otras 20 min), acotado por el maximo absoluto (AP-0162).
        # El claim abs_exp fija el techo absoluto para que la renovacion no lo supere.
        expira_min: int = self._jwt_expire_minutes
        if self._politica is not None:
            payload["canal"] = self._politica.es_canal(roles)
            payload["abs_exp"] = ahora + self._jwt_expire_minutes * 60
            expira_min = min(self._politica.limite_minutos(roles), self._jwt_expire_minutes)
        return self._jwt.encode(payload, expires_minutes=expira_min)

    def renovar_token(self, claims: dict[str, object]) -> str:
        """AP-0129: renueva la sesion por actividad. Reemite un token corto (nuevo jti,
        mismo tv) deslizando el limite de inactividad, sin superar el techo absoluto
        (abs_exp) que se preserva del token original."""
        ahora: int = int(time.time())
        abs_exp_raw: object = claims.get("abs_exp", 0)
        abs_exp: int = int(abs_exp_raw) if isinstance(abs_exp_raw, int) else 0
        roles_raw: object = claims.get("roles", [])
        roles: list[str] = (
            [str(rol) for rol in roles_raw if isinstance(rol, str)]
            if isinstance(roles_raw, list)
            else []
        )
        tv_raw: object = claims.get("tv", 1)
        epoch_raw: object = claims.get("auth_epoch", ahora)
        sid_raw: object = claims.get("sid", "")
        payload: dict[str, object] = {
            "sub": str(claims.get("sub", "")),
            "nombre": claims.get("nombre", ""),
            "roles": roles,
            "jti": secrets.token_urlsafe(16),
            # AP-0130: el sid se preserva (identifica la sesion en el registro, no el token).
            "sid": sid_raw if isinstance(sid_raw, str) else "",
            "tv": tv_raw if isinstance(tv_raw, int) else 1,
            "auth_epoch": epoch_raw if isinstance(epoch_raw, int) else ahora,
            "amr": claims.get("amr", ["pwd"]),
        }
        expira_min: int = self._jwt_expire_minutes
        if self._politica is not None and abs_exp:
            payload["canal"] = self._politica.es_canal(roles)
            payload["abs_exp"] = abs_exp
            restante_min: int = max(1, (abs_exp - ahora) // 60)
            expira_min = min(self._politica.limite_minutos(roles), restante_min)
        return self._jwt.encode(payload, expires_minutes=expira_min)

    def verificar_token(self, token: str) -> dict[str, object]:
        return self._jwt.decode(token)

    # -- Contrasena -----------------------------------------------------------

    async def cambiar_password_async(
        self,
        uid: int,
        password_actual: str,
        nueva_password: str,
        usuario_repo: UsuarioRepository,
        validador: ValidadorPassword | None = None,
        valores_contextuales: Sequence[str] | None = None,
        historial: PasswordHistoryRepository | None = None,
        historial_tamano: int = PASSWORD_HISTORIAL_TAMANO_DEFECTO,
    ) -> None:
        """Cambia la contrasena tras re-autenticar con la actual (AP-0020).

        Aplica validacion contextual via ValidadorPassword cuando se inyecta (AP-0159):
        la contrasena no puede coincidir con el nombre de usuario u otros datos del perfil.
        La validacion de blacklist estatica ya ocurre en el schema antes de llegar aqui.
        Si se inyecta historial (AP-0041) rechaza reutilizar las ultimas N y registra el
        nuevo hash de forma atomica con el cambio.
        """
        usuario: UsuarioEntity | None = await usuario_repo.obtener_por_uid_async(uid)
        if usuario is None or self._verificar(password_actual, usuario) is None:
            raise CredencialesInvalidas("La contrasena actual es incorrecta")

        # AP-0159: verificacion contextual (contrasena != nombre de usuario, cedula, etc.)
        if validador is not None:
            validador.validar(nueva_password, valores_contextuales)

        # AP-0041: no reutilizar las ultimas N contrasenas (incluye la vigente).
        await self._rechazar_si_reutilizada(
            uid, nueva_password, usuario.new_pass_hash, historial, historial_tamano
        )

        nuevo_hash: str = self._hasher.hashear(nueva_password)
        await usuario_repo.actualizar_password_async(uid, nuevo_hash)
        # AP-0041: se archiva el hash que se retira (la contrasena vigente hasta ahora);
        # el nuevo queda como vigente y se compara aparte en el proximo cambio.
        await self._registrar_en_historial(
            uid, usuario.new_pass_hash, historial, historial_tamano
        )

    async def establecer_password_async(
        self,
        uid: int,
        nueva_password: str,
        usuario_repo: UsuarioRepository,
        validador: ValidadorPassword | None = None,
        valores_contextuales: Sequence[str] | None = None,
        hash_actual: str | None = None,
        historial: PasswordHistoryRepository | None = None,
        historial_tamano: int = PASSWORD_HISTORIAL_TAMANO_DEFECTO,
    ) -> None:
        """Establece una nueva contrasena SIN re-autenticar (AP-0038).

        Se usa cuando la identidad ya se verifico antes (p. ej. el cambio autonomo por
        vencimiento, que autentica con la contrasena vencida via autenticar_async). Aplica
        la validacion contextual (AP-0159), rechaza que la nueva coincida con la actual y,
        si se inyecta historial (AP-0041), rechaza reutilizar las ultimas N y la registra.
        """
        if validador is not None:
            validador.validar(nueva_password, valores_contextuales)
        if hash_actual and self._hasher.verificar(nueva_password, hash_actual):
            raise PasswordInsegura(
                "La nueva contrasena no puede ser igual a la actual."
            )
        await self._rechazar_si_reutilizada(
            uid, nueva_password, hash_actual, historial, historial_tamano
        )
        nuevo_hash_nuevo: str = self._hasher.hashear(nueva_password)
        await usuario_repo.actualizar_password_async(uid, nuevo_hash_nuevo)
        # AP-0041: se archiva la contrasena que se retira (la vencida vigente hasta ahora).
        await self._registrar_en_historial(
            uid, hash_actual, historial, historial_tamano
        )

    async def _rechazar_si_reutilizada(
        self,
        uid: int,
        nueva_password: str,
        hash_actual: str | None,
        historial: PasswordHistoryRepository | None,
        tamano: int,
    ) -> None:
        # AP-0041: compara contra las ultimas N usadas (historial mas hash vigente).
        # bcrypt sala cada hash, asi que hay que verificar una por una; se corre en un
        # hilo aparte para no bloquear el event loop y con corte temprano.
        if historial is None:
            return
        recientes: list[str] = list(await historial.ultimos_hashes(uid, tamano))
        if hash_actual and hash_actual not in recientes:
            recientes.append(hash_actual)
        if not recientes:
            return
        coincide: bool = await asyncio.to_thread(
            self._alguna_coincide, nueva_password, recientes
        )
        if coincide:
            raise PasswordReutilizada(tamano)

    def _alguna_coincide(self, nueva_password: str, hashes: list[str]) -> bool:
        for hash_almacenado in hashes:
            if self._hasher.verificar(nueva_password, hash_almacenado):
                return True
        return False

    async def _registrar_en_historial(
        self,
        uid: int,
        hash_retirado: str | None,
        historial: PasswordHistoryRepository | None,
        tamano: int,
    ) -> None:
        # AP-0041: archiva el hash que deja de ser vigente. La contrasena legacy inicial
        # (fijada fuera de este sistema) queda registrada al retirarse en el primer cambio.
        if historial is None or not hash_retirado:
            return
        creado_iso: str = datetime.now(UTC).replace(tzinfo=None).isoformat()
        await historial.insertar(uid, hash_retirado, creado_iso)
        await historial.podar(uid, tamano)

    # -- Autenticacion --------------------------------------------------------

    async def autenticar_async(
        self,
        nombre: str,
        password: str,
        usuario_repo: UsuarioRepository,
    ) -> UsuarioEntity | None:
        """Autentica por nombre de usuario (dbo.users.name). La columna pass es read-only."""
        usuario: UsuarioEntity | None = await usuario_repo.obtener_por_nombre_async(nombre)
        # AP-0160: siempre ejecutar bcrypt para igualar tiempos de respuesta.
        # Si el usuario no existe o no tiene hash new_pass, se usa comparacion dummy.
        if usuario is None or not usuario.new_pass_hash:
            self._hasher.verificar_dummy(password)
            return None
        return self._verificar(password, usuario)

    # -- Privado --------------------------------------------------------------

    def _verificar(self, password: str, usuario: UsuarioEntity) -> UsuarioEntity | None:
        """Verifica unicamente contra new_pass (bcrypt). pass es read-only."""
        if not usuario.new_pass_hash:
            return None
        if self._hasher.verificar(password, usuario.new_pass_hash):
            return usuario
        return None
