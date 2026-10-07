"""Contenedor de inyección de dependencias (FastAPI Depends)."""
import asyncio
import base64
import secrets
from collections.abc import AsyncGenerator, Awaitable, Callable
from functools import lru_cache
from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from jose import jwt as jose_jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.auditor_acceso_objeto import AuditorAccesoObjeto
from src.application.services.auth_service import AuthService
from src.application.services.authorization_service import AuthorizationService
from src.application.services.login_throttle_service import LoginThrottleService
from src.application.services.ownership_validator import OwnershipValidator
from src.application.services.permission_evaluator import PermissionEvaluator
from src.application.services.resolvedor_credencial_bd import ResolvedorCredencialBd
from src.application.services.servicio_alerta_seguridad import ServicioAlertaSeguridad
from src.application.services.servicio_auditoria import ServicioAuditoria
from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.services.servicio_bloqueo_duro import ServicioBloqueoDuro
from src.application.services.servicio_custodia_compartida import ServicioCustodiaCompartida
from src.application.services.servicio_dispositivo import ServicioDispositivo
from src.application.services.servicio_expiracion_password import ServicioExpiracionPassword
from src.application.services.servicio_otp_login import ServicioOtpLogin
from src.application.services.servicio_ownership import ServicioOwnership
from src.application.services.servicio_password_temporal import ServicioPasswordTemporal
from src.application.services.servicio_sesiones import ServicioSesiones
from src.application.services.servicio_verificacion_integridad import (
    ServicioVerificacionIntegridad,
)
from src.application.services.throttle_humano_service import ThrottleHumanoService
from src.application.services.validador_sesion import ValidadorSesion
from src.application.services.validador_token_estandar import ValidadorTokenEstandar
from src.application.services.verificador_permisos_objeto import (
    VerificadorPermisosObjeto,
)
from src.application.services.verificador_privilegio_bd import (
    VerificadorPrivilegioBd,
)
from src.application.use_cases.asesor_consumo_use_case import AsesorConsumoUseCase
from src.application.use_cases.asesor_movilidad_use_case import AsesorMovilidadUseCase
from src.application.use_cases.autorizacion_oob_use_case import AutorizacionOobUseCase
from src.application.use_cases.cambiar_password_expirada_use_case import (
    CambiarPasswordExpiradaUseCase,
)
from src.application.use_cases.cambiar_password_temporal_use_case import (
    CambiarPasswordTemporalUseCase,
)
from src.application.use_cases.completar_login_otp_use_case import CompletarLoginOtpUseCase
from src.application.use_cases.consultar_mi_historial_use_case import (
    ConsultarMiHistorialUseCase,
)
from src.application.use_cases.emitir_password_temporal_use_case import (
    EmitirPasswordTemporalUseCase,
)
from src.application.use_cases.emitir_token_oauth_use_case import EmitirTokenOAuthUseCase
from src.application.use_cases.emitir_token_oidc_use_case import EmitirTokenOidcUseCase
from src.application.use_cases.enviar_correo_masivo_use_case import EnviarCorreoMasivoUseCase
from src.application.use_cases.firma_digital_use_case import FirmaDigitalUseCase
from src.application.use_cases.generar_reportes_use_case import GenerarReportesUseCase
from src.application.use_cases.generar_token_sapin_use_case import GenerarTokenSAPINUseCase
from src.application.use_cases.gestionar_admin_programas_use_case import (
    GestionarAdminProgramasUseCase,
)
from src.application.use_cases.gestionar_admin_subprogramas_use_case import (
    GestionarAdminSubprogramasUseCase,
)
from src.application.use_cases.gestionar_afp_use_case import GestionarAfpUseCase
from src.application.use_cases.gestionar_arl_use_case import GestionarArlUseCase
from src.application.use_cases.gestionar_asignacion_roles_use_case import (
    GestionarAsignacionRolesUseCase,
)
from src.application.use_cases.gestionar_autorizaciones_use_case import (
    GestionarAutorizacionesUseCase,
)
from src.application.use_cases.gestionar_bancos_use_case import GestionarBancosUseCase
from src.application.use_cases.gestionar_canales_use_case import GestionarCanalesUseCase
from src.application.use_cases.gestionar_ciudades_use_case import GestionarCiudadesUseCase
from src.application.use_cases.gestionar_departamentos_use_case import GestionarDepartamentosUseCase
from src.application.use_cases.gestionar_documentos_use_case import GestionarDocumentosUseCase
from src.application.use_cases.gestionar_ejecutivos_use_case import GestionarEjecutivosUseCase
from src.application.use_cases.gestionar_eps_use_case import GestionarEpsUseCase
from src.application.use_cases.gestionar_oficinas_use_case import GestionarOficinasUseCase
from src.application.use_cases.gestionar_profesiones_use_case import GestionarProfesionesUseCase
from src.application.use_cases.gestionar_referencias_use_case import GestionarReferenciasUseCase
from src.application.use_cases.gestionar_usuarios_use_case import GestionarUsuariosUseCase
from src.application.use_cases.login_use_case import LoginUseCase
from src.application.use_cases.mi_perfil_use_case import MiPerfilUseCase
from src.application.use_cases.obtener_politica_retencion_use_case import (
    ObtenerPoliticaRetencionUseCase,
)
from src.application.use_cases.obtener_preview_reportes_use_case import (
    ObtenerPreviewReportesUseCase,
)
from src.application.use_cases.verificar_email_use_case import VerificarEmailUseCase
from src.application.use_cases.verificar_integridad_cadena_use_case import (
    VerificarIntegridadCadenaUseCase,
)
from src.application.use_cases.verificar_sincronizacion_horaria_use_case import (
    VerificarSincronizacionHorariaUseCase,
)
from src.domain.exceptions.cuenta_bloqueada import CuentaBloqueada
from src.domain.exceptions.secreto_no_disponible import SecretoNoDisponible
from src.domain.exceptions.sesion_invalida import SesionInvalida
from src.domain.exceptions.token_invalido import TokenInvalido
from src.domain.exceptions.token_oidc_invalido import TokenOidcInvalido
from src.domain.ports.outbound.almacen_efimero_distribuido import AlmacenEfimeroDistribuido
from src.domain.ports.outbound.estado_credencial_repository import EstadoCredencialRepository
from src.domain.ports.outbound.gestor_clave_maestra import GestorClaveMaestra
from src.domain.ports.outbound.notificador_correo import NotificadorCorreo
from src.domain.ports.outbound.notificador_evento_seguridad import (
    NotificadorEventoSeguridad,
)
from src.domain.ports.outbound.proveedor_secretos import ProveedorSecretos
from src.domain.ports.outbound.reloj_oficial import RelojOficial
from src.domain.ports.outbound.revocacion_token_store import RevocacionTokenStore
from src.domain.ports.outbound.sanitizador_metadatos import SanitizadorMetadatos
from src.domain.ports.outbound.sonda_disponibilidad import SondaDisponibilidad
from src.domain.services.cifrador_sapin_versionado import CifradorSapinVersionado
from src.domain.services.clasificador_criticidad import ClasificadorCriticidad
from src.domain.services.clasificador_retencion import ClasificadorRetencion
from src.domain.services.crypto_sapin import CryptoSAPIN
from src.domain.services.politica_expiracion_password import PoliticaExpiracionPassword
from src.domain.services.politica_inactividad import PoliticaInactividad
from src.domain.services.politica_password_temporal import PoliticaPasswordTemporal
from src.domain.services.politica_sesiones import PoliticaSesiones
from src.domain.services.validador_password import ValidadorPassword
from src.domain.services.verificador_cadena import VerificadorCadena
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.infrastructure.config.settings import Settings
from src.infrastructure.external.cadena_email_notifier import CadenaEmailNotifier
from src.infrastructure.external.console_email_notifier import ConsoleEmailNotifier
from src.infrastructure.external.in_memory_almacen_efimero import InMemoryAlmacenEfimero
from src.infrastructure.external.in_memory_bloqueo_cuenta_repo import InMemoryBloqueoCuentaRepo
from src.infrastructure.external.in_memory_bloqueo_duro_repo import InMemoryBloqueoDuroRepo
from src.infrastructure.external.in_memory_codigo_store import InMemoryCodigoStore
from src.infrastructure.external.in_memory_desafio_oob_store import InMemoryDesafioOobStore
from src.infrastructure.external.in_memory_desafio_otp_store import InMemoryDesafioOtpStore
from src.infrastructure.external.in_memory_dispositivo_repo import InMemoryDispositivoRepo
from src.infrastructure.external.in_memory_estado_credencial_repo import (
    InMemoryEstadoCredencialRepo,
)
from src.infrastructure.external.in_memory_evidencia_firma_store import InMemoryEvidenciaFirmaStore
from src.infrastructure.external.in_memory_intentos_login_store import InMemoryIntentosLoginStore
from src.infrastructure.external.in_memory_revocacion_token_store import (
    InMemoryRevocacionTokenStore,
)
from src.infrastructure.external.in_memory_sesion_repo import InMemorySesionRepo
from src.infrastructure.external.notificador_correo_alerta import NotificadorCorreoAlerta
from src.infrastructure.external.notificador_log_alerta import NotificadorLogAlerta
from src.infrastructure.external.notificador_webhook import NotificadorWebhook
from src.infrastructure.external.redis_almacen_efimero import RedisAlmacenEfimero
from src.infrastructure.external.reloj_oficial_http import RelojOficialHttp
from src.infrastructure.external.smtp_email_notifier import SmtpEmailNotifier
from src.infrastructure.files.sanitizador_metadatos_archivo import SanitizadorMetadatosArchivo
from src.infrastructure.logging.alerta_handler import AlertaHandler
from src.infrastructure.logging.security_audit import SecurityAuditLogger
from src.infrastructure.persistence.database import get_db_session_async, get_session_factory
from src.infrastructure.persistence.repositories.sql_server_sonda_disponibilidad import (
    SqlServerSondaDisponibilidad,
)
from src.infrastructure.persistence.repositories.sql_server_sonda_permisos_objeto import (
    SqlServerSondaPermisosObjeto,
)
from src.infrastructure.persistence.repositories.sql_server_sonda_privilegio_bd import (
    SqlServerSondaPrivilegioBd,
)
from src.infrastructure.persistence.repositories.sqlalchemy_admin_programa_repo import (
    SQLAlchemyAdminProgramaRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_admin_subprograma_repo import (
    SQLAlchemyAdminSubprogramaRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_afp_repo import SQLAlchemyAfpRepo
from src.infrastructure.persistence.repositories.sqlalchemy_arl_repo import SQLAlchemyArlRepo
from src.infrastructure.persistence.repositories.sqlalchemy_asesor_consumo_repo import (
    SQLAlchemyAsesorConsumoRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_asesor_movilidad_repo import (
    SQLAlchemyAsesorMovilidadRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_asignacion_roles_repo import (
    SQLAlchemyAsignacionRolesRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_auditoria_escritor_gateway import (
    SqlAlchemyAuditoriaEscritorGateway,
)
from src.infrastructure.persistence.repositories.sqlalchemy_auditoria_lector_repo import (
    SqlAlchemyAuditoriaLectorRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_autorizaciones_repo import (
    SQLAlchemyAutorizacionesRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_banco_repo import SQLAlchemyBancoRepo
from src.infrastructure.persistence.repositories.sqlalchemy_canal_oficina_repo import (
    SQLAlchemyCanalOficinaRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_canal_repo import SQLAlchemyCanalRepo
from src.infrastructure.persistence.repositories.sqlalchemy_ciudad_repo import SQLAlchemyCiudadRepo
from src.infrastructure.persistence.repositories.sqlalchemy_departamento_repo import (
    SQLAlchemyDepartamentoRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_documento_repo import (
    SQLAlchemyDocumentoRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_eps_repo import SQLAlchemyEpsRepo
from src.infrastructure.persistence.repositories.sqlalchemy_estado_credencial_repo import (
    SQLAlchemyEstadoCredencialRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_frontend_modules_repo import (
    SQLAlchemyFrontendModulesRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_historico_correo_repo import (
    SQLAlchemyHistoricoCorreoRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_oficina_repo import (
    SQLAlchemyOficinaRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_password_expiracion_repo import (
    SqlAlchemyPasswordExpiracionRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_password_history_repo import (
    SqlAlchemyPasswordHistoryRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_password_temporal_repo import (
    SqlAlchemyPasswordTemporalRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_perfil_repo import SQLAlchemyPerfilRepo
from src.infrastructure.persistence.repositories.sqlalchemy_profesion_repo import (
    SQLAlchemyProfesionRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_referencia_repo import (
    SQLAlchemyReferenciaRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_revocacion_token_repo import (
    SQLAlchemyRevocacionTokenRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_users_ejecutivo_repo import (
    SQLAlchemyUsersEjecutivoRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_usuario_repo import (
    SQLAlchemyUsuarioRepo,
)
from src.infrastructure.reporting.excel_report_generator import ExcelReportGenerator
from src.infrastructure.security.aes_gcm_field_cipher import AesGcmFieldCipher
from src.infrastructure.security.cliente_pam_http import ClientePamHttp
from src.infrastructure.security.firmador_es256 import FirmadorEs256
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.kms_aws import KmsAws
from src.infrastructure.security.kms_local_software import KmsLocalSoftware
from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.security.proveedor_clave_oidc_es256 import ProveedorClaveOidcEs256
from src.infrastructure.security.proveedor_secretos_entorno import ProveedorSecretosEntorno
from src.infrastructure.security.proveedor_secretos_pam import ProveedorSecretosPam
from src.infrastructure.security.shamir_custodia_compartida import ShamirCustodiaCompartida
from src.infrastructure.security.verificador_integridad_archivos import (
    VerificadorIntegridadArchivos,
)
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD
from src.shared.constants.kms import KMS_PROVIDER_LOCAL
from src.shared.constants.oidc import ALGORITMOS_OIDC_PERMITIDOS
from src.shared.constants.password_blacklist import BLACKLIST_COMUNES
from src.shared.constants.secretos import (
    PROVEEDOR_SECRETOS_PAM,
    SECRETO_DB_PASSWORD,
    SECRETO_DB_USER,
)

_bearer_scheme: HTTPBearer = HTTPBearer(auto_error=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_security_audit_logger() -> SecurityAuditLogger:
    """Logger de auditoría de seguridad (AP-0022), singleton de proceso."""
    return SecurityAuditLogger()


async def get_db_session_opcional() -> AsyncGenerator[AsyncSession | None, None]:
    """AP-0049: sesion de BD para la validacion viva de require_token.

    Devuelve None si la BD no esta inicializada (apps minimas de prueba sin
    lifespan): la validacion degrada al comportamiento AP-0021 (adaptadores en
    memoria, sin chequeo vivo), sin romper la resolucion de dependencias."""
    try:
        async for sesion_bd in get_db_session_async():
            yield sesion_bd
            return
    except RuntimeError:
        yield None


async def require_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer_scheme),
    settings: Settings = Depends(get_settings),
    session: AsyncSession | None = Depends(get_db_session_opcional),
) -> dict:
    """Valida el JWT tomado de la cabecera Bearer o, en su defecto, de la cookie de
    sesión HttpOnly (Medida A). Lanza 401 si falta o es inválido."""
    token_str: str | None = None
    if credentials is not None:
        token_str = credentials.credentials
    else:
        token_str = request.cookies.get(settings.cookie_auth_name)
    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # AP-0010: si el token es estandar OIDC (asimetrico), se valida via JWKS (iss, aud, firma).
    if settings.oidc_enabled:
        try:
            encabezado: dict[str, object] = jose_jwt.get_unverified_header(token_str)
        except JWTError:
            encabezado = {}
        if str(encabezado.get("alg", "")) in ALGORITMOS_OIDC_PERMITIDOS:
            try:
                claims_oidc: dict[str, object] = (
                    get_validador_token_estandar().validar(token_str)
                )
            except TokenOidcInvalido as exc_oidc:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token OIDC invalido o revocado",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from exc_oidc
            # AP-0208: el token estandar NO evade la revocacion. Se valida igual que el
            # JWT propio (token_version, sid revocado, usuario bloqueado o inhabilitado):
            # asi un cambio de contrasena tambien lo invalida en las apps SSO, y se
            # restaura AP-0133 sobre esta ruta.
            if settings.sesion_validacion_enabled:
                try:
                    await get_validador_sesion(session).validar(claims_oidc)
                except CuentaBloqueada as exc_ses_oidc:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cuenta bloqueada",
                    ) from exc_ses_oidc
                except SesionInvalida as exc_ses_oidc2:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Sesion invalida o revocada",
                        headers={"WWW-Authenticate": "Bearer"},
                    ) from exc_ses_oidc2
            return claims_oidc
    try:
        payload: dict[str, object] = JWTHandler(
            settings.jwt_secret_key, settings.jwt_algorithm
        ).decode(token_str)
        if settings.sesion_validacion_enabled:
            try:
                await get_validador_sesion(session).validar(payload)
            except CuentaBloqueada as exc_sesion:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cuenta bloqueada",
                ) from exc_sesion
            except SesionInvalida as exc_sesion:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Sesion invalida o revocada",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from exc_sesion
        return payload
    except TokenInvalido as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


TokenDep = Annotated[dict, Depends(require_token)]


SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_db_session_async)]


@lru_cache
def get_sanitizador_metadatos() -> SanitizadorMetadatos:
    """AP-0085: sanitizador de metadatos de archivos (singleton de proceso)."""
    return SanitizadorMetadatosArchivo()


SanitizadorMetadatosDep = Annotated[
    SanitizadorMetadatos, Depends(get_sanitizador_metadatos)
]


@lru_cache
def get_field_cipher() -> AesGcmFieldCipher:
    """Cifrador de campos restringidos (Medida C — AP-0147/AP-0095). Singleton:
    construye el registro de claves (activa + retiradas) una sola vez."""
    settings: Settings = get_settings()
    if settings.app_encryption_key_wrapped:
        # AP-0180: la DEK del cifrado de campos se desenvuelve con el KMS o HSM;
        # el KEK nunca entra al proceso.
        gestor: GestorClaveMaestra = get_gestor_clave_maestra()
        dek: bytes = gestor.descifrar_clave_datos(
            base64.b64decode(settings.app_encryption_key_wrapped)
        )
        return AesGcmFieldCipher(
            {settings.app_encryption_key_id: dek}, settings.app_encryption_key_id
        )
    if not settings.app_encryption_key:
        raise RuntimeError(
            "APP_ENCRYPTION_KEY no configurada — el cifrado de campos restringidos es requerido"
        )
    claves: dict[int, bytes] = {
        settings.app_encryption_key_id: base64.b64decode(settings.app_encryption_key)
    }
    if settings.app_encryption_keys_retired:
        for par in settings.app_encryption_keys_retired.split(","):
            kid_str, b64 = par.split(":", 1)
            claves[int(kid_str)] = base64.b64decode(b64)
    return AesGcmFieldCipher(claves, settings.app_encryption_key_id)


def _build_crypto(settings: Settings) -> CryptoSAPIN | None:
    if not settings.sapin_aes_key_ctr:
        return None
    return CryptoSAPIN(
        aes_key_ctr=base64.b64decode(settings.sapin_aes_key_ctr),
        aes_iv_ctr=base64.b64decode(settings.sapin_aes_iv_ctr),
        aes_key_cbc=base64.b64decode(settings.sapin_aes_key_cbc),
    )


def _build_cifrador_sapin(settings: Settings) -> CifradorSapinVersionado | None:
    """AP-0075: emisor versionado del token SAPIN (v1 AES-128-CTR legacy, v2 AES-256-GCM)."""
    crypto: CryptoSAPIN | None = _build_crypto(settings)
    if crypto is None:
        return None
    clave_gcm: bytes | None = (
        base64.b64decode(settings.sapin_aes_key_gcm) if settings.sapin_aes_key_gcm else None
    )
    return CifradorSapinVersionado(crypto, clave_gcm, settings.sapin_token_version)


def _build_gestor_clave_maestra(settings: Settings) -> GestorClaveMaestra:
    # AP-0180: selecciona el custodio del KEK. local es solo desarrollo o pruebas;
    # el guard de Settings exige un proveedor HSM o KMS en staging y produccion.
    if settings.kms_provider == KMS_PROVIDER_LOCAL:
        if settings.custodia_doble_enabled:
            # AP-0015: la KEK se reconstruye por doble custodia (Shamir); ninguna
            # persona sola la posee. Con menos del umbral de shares, el arranque falla.
            shares_custodia: list[str] = [
                fragmento
                for fragmento in settings.custodia_shares.split(",")
                if fragmento.strip()
            ]
            kek: bytes = get_servicio_custodia_compartida().reconstruir_kek(
                shares_custodia
            )
        elif settings.kms_local_master_key:
            kek = base64.b64decode(settings.kms_local_master_key)
        else:
            kek = secrets.token_bytes(32)
        return KmsLocalSoftware(kek)
    return KmsAws(settings.kms_key_id)


@lru_cache
def get_gestor_clave_maestra() -> GestorClaveMaestra:
    return _build_gestor_clave_maestra(get_settings())


def get_usuario_repo(session: SessionDep) -> SQLAlchemyUsuarioRepo:
    return SQLAlchemyUsuarioRepo(session)


def get_frontend_modules_repo(session: SessionDep) -> SQLAlchemyFrontendModulesRepo:
    return SQLAlchemyFrontendModulesRepo(session)


def get_auth_service(settings: SettingsDep) -> AuthService:
    politica: PoliticaInactividad | None = None
    if settings.idle_timeout_enabled:
        # AP-0129: la politica fija el TTL del token por inactividad segun los roles.
        roles_canal: frozenset[str] = frozenset(
            r.strip() for r in settings.idle_roles_canal.split(",") if r.strip()
        )
        politica = PoliticaInactividad(
            minutos_canal=settings.idle_timeout_canal_min,
            minutos_otras=settings.idle_timeout_otras_min,
            roles_canal=roles_canal,
        )
    return AuthService(
        jwt_handler=JWTHandler(settings.jwt_secret_key, settings.jwt_algorithm),
        password_hasher=PasswordHasher(),
        jwt_expire_minutes=settings.jwt_expire_minutes,
        crypto_sapin=_build_crypto(settings),
        politica_inactividad=politica,
    )



@lru_cache(maxsize=1)
def get_validador_password() -> ValidadorPassword:
    """AP-0159: singleton — carga la blacklist una sola vez al inicio."""
    return ValidadorPassword(blacklist=BLACKLIST_COMUNES)
# ── Anti fuerza bruta de login (AP-0007) ─────────────────────────────────────


@lru_cache
def get_intentos_login_store() -> InMemoryIntentosLoginStore:
    """Almacén del conteo de fallos de login, singleton de proceso (comparte estado
    entre peticiones). TTL = ventana de reinicio del contador."""
    settings: Settings = get_settings()
    return InMemoryIntentosLoginStore(ttl_segundos=settings.login_intentos_ttl_seg)


@lru_cache
def get_login_throttle() -> LoginThrottleService:
    """Servicio de retraso incremental (AP-0007), singleton sobre el store de proceso."""
    settings: Settings = get_settings()
    return LoginThrottleService(
        store=get_intentos_login_store(),
        paso_segundos=settings.login_retraso_paso_seg,
        maximo_segundos=settings.login_retraso_max_seg,
    )


def get_login_uc(session: SessionDep, settings: SettingsDep) -> LoginUseCase:
    return LoginUseCase(
        auth_service=get_auth_service(settings),
        throttle=get_login_throttle(),
        usuario_repo=SQLAlchemyUsuarioRepo(session),
        modulos_repo=SQLAlchemyFrontendModulesRepo(session),
        bloqueo=get_servicio_bloqueo_cuenta(),
        bloqueo_duro=get_servicio_bloqueo_duro(),
        estado_credencial=get_estado_credencial_repo_sesion(session),
        otp=get_servicio_otp_login(),
        expiracion=get_servicio_expiracion_password(session),
        enforcement_enabled=settings.password_vencimiento_enforcement_enabled,
        password_temporal=get_servicio_password_temporal(session),
    )


def extraer_ip_cliente(request: Request, settings: Settings) -> str:
    """IP del cliente para el throttling (AP-0007 / AP-0019).

    Tras un proxy de confianza (IIS/ELB) la IP real va en X-Forwarded-For; solo se
    lee si `trust_proxy_headers` está activo, para no fiarse de una cabecera
    falsificable cuando el backend queda expuesto directamente.
    """
    if settings.trust_proxy_headers:
        xff: str | None = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
    return request.client.host if request.client else "desconocida"


# ── Gating de humano por retrasos incrementales (AP-0019) ─────────────────────


@lru_cache
def get_throttle_humano_store() -> InMemoryIntentosLoginStore:
    """Store del contador de intentos por acción+IP, singleton de proceso."""
    settings: Settings = get_settings()
    return InMemoryIntentosLoginStore(ttl_segundos=settings.throttle_humano_ttl_seg)


@lru_cache
def get_throttle_humano() -> ThrottleHumanoService:
    settings: Settings = get_settings()
    return ThrottleHumanoService(
        store=get_throttle_humano_store(),
        intentos_libres=settings.throttle_humano_free_intentos,
        paso_segundos=settings.throttle_humano_paso_seg,
        maximo_segundos=settings.throttle_humano_max_seg,
    )


def require_throttle_humano(accion: str) -> Callable[..., Awaitable[None]]:
    """Fábrica de dependencia FastAPI: aplica retraso incremental por acción+IP.

    Uso: `dependencies=[Depends(require_throttle_humano("registro"))]` en un router
    público. No bloquea el event loop (asyncio.sleep) ni distingue éxito/fallo —
    throttlea el volumen de peticiones por IP para gatear bots (AP-0019).
    """

    async def _dependencia(request: Request, settings: SettingsDep) -> None:
        ip: str = extraer_ip_cliente(request, settings)
        clave: str = f"{accion}|{ip}"
        espera_segundos: int = await get_throttle_humano().registrar_intento_async(clave)
        if espera_segundos > 0:
            await asyncio.sleep(espera_segundos)

    return _dependencia


def get_token_sapin_uc(session: SessionDep, settings: SettingsDep) -> GenerarTokenSAPINUseCase:
    cifrador = _build_cifrador_sapin(settings)
    if cifrador is None:
        raise RuntimeError("SAPIN crypto no configurado — revisar variables de entorno sapin_*")
    return GenerarTokenSAPINUseCase(
        cifrador=cifrador,
        perfil_repo=SQLAlchemyPerfilRepo(session, get_field_cipher()),
        url_sapin=settings.sapin_url,
    )


def get_reportes_uc(session: SessionDep) -> GenerarReportesUseCase:
    generador: ExcelReportGenerator = ExcelReportGenerator(session, get_field_cipher())
    return GenerarReportesUseCase(reporte_generator=generador)


def get_preview_reportes_uc(session: SessionDep) -> ObtenerPreviewReportesUseCase:
    generador: ExcelReportGenerator = ExcelReportGenerator(session, get_field_cipher())
    return ObtenerPreviewReportesUseCase(reporte_generator=generador)


def get_documentos_uc(session: SessionDep) -> GestionarDocumentosUseCase:
    return GestionarDocumentosUseCase(
        documento_repo=SQLAlchemyDocumentoRepo(session, get_field_cipher()),
    )


def get_authorization_service(session: SessionDep) -> AuthorizationService:
    """AP-0055: punto unico de autorizacion a nivel de objeto (BOLA/IDOR)."""
    settings: Settings = get_settings()
    ownership_validator: OwnershipValidator = OwnershipValidator(
        servicio_ownership=ServicioOwnership(usuario_repo=SQLAlchemyUsuarioRepo(session)),
        desafio_store=get_desafio_oob_store(),
    )
    return AuthorizationService(
        permission_evaluator=PermissionEvaluator(),
        ownership_validator=ownership_validator,
        auditor=AuditorAccesoObjeto(get_servicio_auditoria()),
        modo=settings.object_authz_mode,
    )


def get_referencias_uc(session: SessionDep) -> GestionarReferenciasUseCase:
    return GestionarReferenciasUseCase(referencia_repo=SQLAlchemyReferenciaRepo(session))


def get_ejecutivos_uc(session: SessionDep) -> GestionarEjecutivosUseCase:
    return GestionarEjecutivosUseCase(ejecutivo_repo=SQLAlchemyUsersEjecutivoRepo(session))


def get_canales_uc(session: SessionDep) -> GestionarCanalesUseCase:
    return GestionarCanalesUseCase(
        canal_repo=SQLAlchemyCanalRepo(session),
        canal_oficina_repo=SQLAlchemyCanalOficinaRepo(session),
    )


def get_oficinas_uc(session: SessionDep) -> GestionarOficinasUseCase:
    return GestionarOficinasUseCase(
        oficina_repo=SQLAlchemyOficinaRepo(session),
        canal_oficina_repo=SQLAlchemyCanalOficinaRepo(session),
    )


def get_asesor_consumo_uc(session: SessionDep) -> AsesorConsumoUseCase:
    return AsesorConsumoUseCase(
        asesor_repo=SQLAlchemyAsesorConsumoRepo(session, get_field_cipher()),
        perfil_repo=SQLAlchemyPerfilRepo(session, get_field_cipher()),
    )


def get_asesor_movilidad_uc(session: SessionDep) -> AsesorMovilidadUseCase:
    return AsesorMovilidadUseCase(
        asesor_repo=SQLAlchemyAsesorMovilidadRepo(session, get_field_cipher()),
        perfil_repo=SQLAlchemyPerfilRepo(session, get_field_cipher()),
    )


def get_mi_perfil_uc(session: SessionDep) -> MiPerfilUseCase:
    return MiPerfilUseCase(
        usuario_repo=SQLAlchemyUsuarioRepo(session),
        perfil_repo=SQLAlchemyPerfilRepo(session, get_field_cipher()),
        documento_repo=SQLAlchemyDocumentoRepo(session, get_field_cipher()),
    )


def get_admin_usuarios_uc(session: SessionDep) -> GestionarUsuariosUseCase:
    return GestionarUsuariosUseCase(
        usuario_repo=SQLAlchemyUsuarioRepo(session),
        estado_credencial=get_estado_credencial_repo_sesion(session),
    )


def get_admin_afp_uc(session: SessionDep) -> GestionarAfpUseCase:
    return GestionarAfpUseCase(afp_repo=SQLAlchemyAfpRepo(session))


def get_admin_arl_uc(session: SessionDep) -> GestionarArlUseCase:
    return GestionarArlUseCase(arl_repo=SQLAlchemyArlRepo(session))


def get_admin_eps_uc(session: SessionDep) -> GestionarEpsUseCase:
    return GestionarEpsUseCase(eps_repo=SQLAlchemyEpsRepo(session))


def get_admin_bancos_uc(session: SessionDep) -> GestionarBancosUseCase:
    return GestionarBancosUseCase(banco_repo=SQLAlchemyBancoRepo(session))


def get_admin_profesiones_uc(session: SessionDep) -> GestionarProfesionesUseCase:
    return GestionarProfesionesUseCase(profesion_repo=SQLAlchemyProfesionRepo(session))


def get_admin_departamentos_uc(session: SessionDep) -> GestionarDepartamentosUseCase:
    return GestionarDepartamentosUseCase(departamento_repo=SQLAlchemyDepartamentoRepo(session))


def get_admin_ciudades_uc(session: SessionDep) -> GestionarCiudadesUseCase:
    return GestionarCiudadesUseCase(ciudad_repo=SQLAlchemyCiudadRepo(session))


def get_admin_programas_uc(session: SessionDep) -> GestionarAdminProgramasUseCase:
    return GestionarAdminProgramasUseCase(programa_repo=SQLAlchemyAdminProgramaRepo(session))


def get_admin_subprogramas_uc(session: SessionDep) -> GestionarAdminSubprogramasUseCase:
    return GestionarAdminSubprogramasUseCase(
        subprograma_repo=SQLAlchemyAdminSubprogramaRepo(session)
    )


def get_admin_autorizaciones_uc(session: SessionDep) -> GestionarAutorizacionesUseCase:
    return GestionarAutorizacionesUseCase(
        autorizaciones_repo=SQLAlchemyAutorizacionesRepo(session)
    )


# ── Verificación de propiedad del correo (AP-0004) ───────────────────────────


@lru_cache
def get_codigo_store() -> InMemoryCodigoStore:
    """Almacén OTP en memoria, singleton de proceso (comparte estado entre
    peticiones). TTL = ttl_horas × 3600 s."""
    settings: Settings = get_settings()
    return InMemoryCodigoStore(ttl_segundos=settings.verif_codigo_ttl_horas * 3600)


@lru_cache
def get_notificador_correo() -> NotificadorCorreo:
    """Gateway HTTP si hay `email_api_base_url`; si no, SMTP si hay host; en su
    defecto, notificador de consola (desarrollo)."""
    settings: Settings = get_settings()
    if settings.email_api_base_url:
        return CadenaEmailNotifier(
            base_url=settings.email_api_base_url,
            usuario=settings.email_api_username,
            password=settings.email_api_password,
            customer=settings.email_api_customer,
            product=settings.email_api_product,
            channel=settings.email_api_channel,
            remitente=settings.email_api_sender,
            validar_lista_negra=settings.email_api_validate_blacklist,
            timeout=settings.email_api_timeout,
            verificar_tls=settings.email_api_verify_tls,
        )
    if not settings.smtp_host:
        return ConsoleEmailNotifier()
    return SmtpEmailNotifier(
        host=settings.smtp_host,
        port=settings.smtp_port,
        usuario=settings.smtp_user,
        password=settings.smtp_password,
        remitente=settings.smtp_from,
        usar_starttls=settings.smtp_starttls,
        timeout=settings.smtp_timeout,
    )


def get_enviar_correo_masivo_uc() -> EnviarCorreoMasivoUseCase:
    """AP-0088: caso de uso de correo masivo (destinatarios ocultos, BCC o CCO)."""
    return EnviarCorreoMasivoUseCase(notificador=get_notificador_correo())


@lru_cache
def get_reloj_oficial() -> RelojOficial:
    """AP-0144: reloj externo de hora oficial (singleton de proceso)."""
    settings: Settings = get_settings()
    return RelojOficialHttp(url=settings.hora_oficial_url, timeout=settings.hora_sync_timeout)


def get_verificar_sync_horaria_uc(settings: SettingsDep) -> VerificarSincronizacionHorariaUseCase:
    """AP-0144: caso de uso que compara la hora del sistema con la oficial."""
    return VerificarSincronizacionHorariaUseCase(
        reloj=get_reloj_oficial(), umbral_segundos=settings.hora_drift_max_seg
    )


def get_emitir_token_oauth_uc(settings: SettingsDep) -> EmitirTokenOAuthUseCase:
    """AP-0146: IdP que emite access tokens estilo OAuth para apps de terceros."""
    return EmitirTokenOAuthUseCase(
        jwt_handler=JWTHandler(settings.jwt_secret_key, settings.jwt_algorithm),
        issuer=settings.oauth_issuer,
        audiencias_permitidas=settings.oauth_audiencias_permitidas,
        expire_minutes=settings.oauth_token_expire_minutes,
        scope_default=settings.oauth_scope_default,
    )


def get_verificacion_email_uc(session: SessionDep) -> VerificarEmailUseCase:
    settings: Settings = get_settings()
    return VerificarEmailUseCase(
        perfil_repo=SQLAlchemyPerfilRepo(session, get_field_cipher()),
        codigo_store=get_codigo_store(),
        notificador=get_notificador_correo(),
        historico_repo=SQLAlchemyHistoricoCorreoRepo(session),
        ttl_horas=settings.verif_codigo_ttl_horas,
        max_intentos=settings.verif_codigo_max_intentos,
        cooldown_segundos=settings.verif_reenvio_cooldown_seg,
        frontend_base_url=settings.frontend_base_url,
    )


def get_admin_asignaciones_uc(session: SessionDep) -> GestionarAsignacionRolesUseCase:
    return GestionarAsignacionRolesUseCase(
        asignacion_repo=SQLAlchemyAsignacionRolesRepo(session)
    )


@lru_cache
def get_desafio_oob_store() -> InMemoryDesafioOobStore:
    """AP-0005: almacen de desafios OOB en memoria, singleton de proceso (TTL absoluto)."""
    settings: Settings = get_settings()
    return InMemoryDesafioOobStore(ttl_segundos=settings.oob_codigo_ttl_seg)


def get_autorizacion_oob_uc(session: SessionDep) -> AutorizacionOobUseCase:
    """AP-0005: subsistema de confirmacion OOB de transacciones criticas."""
    settings: Settings = get_settings()
    return AutorizacionOobUseCase(
        usuario_repo=SQLAlchemyUsuarioRepo(session),
        desafio_store=get_desafio_oob_store(),
        notificador=get_notificador_correo(),
        clasificador=ClasificadorCriticidad(),
        max_intentos=settings.oob_max_intentos,
        ttl_segundos=settings.oob_codigo_ttl_seg,
    )


@lru_cache
def get_evidencia_firma_store() -> InMemoryEvidenciaFirmaStore:
    """AP-0006: almacen de evidencias de firma en memoria, singleton de proceso."""
    return InMemoryEvidenciaFirmaStore()


@lru_cache
def get_firmador_digital() -> FirmadorEs256:
    """AP-0006: firmador ES256 singleton. Clave de settings (base64 PEM) o efimera."""
    settings: Settings = get_settings()
    pem: bytes | None = (
        base64.b64decode(settings.firma_private_key_pem)
        if settings.firma_private_key_pem
        else None
    )
    return FirmadorEs256(pem)


def get_firma_digital_uc() -> FirmaDigitalUseCase:
    """AP-0006: subsistema de firma y verificacion digital."""
    return FirmaDigitalUseCase(
        firmador=get_firmador_digital(),
        evidencia_store=get_evidencia_firma_store(),
    )


@lru_cache
def get_verificador_cadena() -> VerificadorCadena:
    """AP-0025: verificador de integridad de la cadena de sellos (sin estado)."""
    return VerificadorCadena()


def get_verificar_cadena_uc() -> VerificarIntegridadCadenaUseCase:
    """AP-0025: caso de uso de verificacion de la cadena de sellos de auditoria."""
    return VerificarIntegridadCadenaUseCase(verificador=get_verificador_cadena())


@lru_cache
def get_clasificador_retencion() -> ClasificadorRetencion:
    """AP-0026: clasificador de retencion con los plazos configurados por entorno."""
    settings: Settings = get_settings()
    return ClasificadorRetencion(settings.retencion_dias_por_categoria())


def get_politica_retencion_uc() -> ObtenerPoliticaRetencionUseCase:
    """AP-0026: caso de uso que expone la politica de retencion vigente."""
    return ObtenerPoliticaRetencionUseCase(clasificador=get_clasificador_retencion())


@lru_cache
def get_servicio_auditoria() -> ServicioAuditoria:
    """AP-0028: servicio de auditoria fail-safe (escritura autonoma en audit_log)."""
    return ServicioAuditoria(
        escritor=SqlAlchemyAuditoriaEscritorGateway(get_session_factory())
    )


def get_servicio_verificacion_integridad() -> ServicioVerificacionIntegridad:
    """AP-0120: servicio de verificacion de integridad de archivos criticos de la app al
    arranque, que reporta el resultado en la bitacora de seguridad. Fail-safe; sin baseline
    configurado no hace nada."""
    settings: Settings = get_settings()
    verificador: VerificadorIntegridadArchivos = VerificadorIntegridadArchivos(
        settings.integridad_baseline_path, settings.integridad_base_dir
    )
    return ServicioVerificacionIntegridad(verificador, settings.integridad_check_enabled)


@lru_cache
def get_almacen_efimero() -> AlmacenEfimeroDistribuido:
    """AP-0081: almacen efimero compartido entre replicas para alta disponibilidad. Con
    redis_url configurada usa el adaptador Redis (estado compartido entre todas las replicas);
    en su defecto, el adaptador en memoria (un solo proceso, dev/test)."""
    settings: Settings = get_settings()
    if settings.redis_url:
        return RedisAlmacenEfimero(settings.redis_url)
    return InMemoryAlmacenEfimero()


def get_sonda_disponibilidad() -> SondaDisponibilidad:
    """AP-0081: sonda de disponibilidad de la base de datos para el endpoint de
    readiness (Kubernetes/balanceador). Usa la fabrica de sesiones autonoma; nunca
    propaga excepciones (degrada a no-disponible)."""
    return SqlServerSondaDisponibilidad(get_session_factory())


def get_verificador_privilegio_bd() -> VerificadorPrivilegioBd:
    """AP-0056: verificador de arranque del privilegio del principal de BD (minimo
    privilegio). Sondea via la fabrica de sesiones autonoma; fail-fast en staging y
    produccion, warning en dev y test; conmutable por `db_privilege_check_enabled`."""
    settings: Settings = get_settings()
    return VerificadorPrivilegioBd(
        sonda=SqlServerSondaPrivilegioBd(get_session_factory()),
        app_env=settings.app_env,
        habilitado=settings.db_privilege_check_enabled,
    )


def get_auditoria_lector_repo(
    session: AsyncSession = Depends(get_db_session_async),
) -> SqlAlchemyAuditoriaLectorRepo:
    """AP-0028: lector del historial ligado a la sesion de la peticion."""
    return SqlAlchemyAuditoriaLectorRepo(session)


def get_consultar_mi_historial_uc(
    lector: SqlAlchemyAuditoriaLectorRepo = Depends(get_auditoria_lector_repo),
) -> ConsultarMiHistorialUseCase:
    """AP-0028: caso de uso de consulta del propio historial."""
    return ConsultarMiHistorialUseCase(lector=lector)


def get_politica_expiracion_password() -> PoliticaExpiracionPassword:
    """AP-0037: politica de vencimiento de contrasena (vigencia y ventana de aviso)."""
    settings: Settings = get_settings()
    return PoliticaExpiracionPassword(
        vigencia_dias=settings.password_vigencia_dias,
        aviso_dias=settings.password_aviso_dias,
        gracia_dias=settings.password_gracia_dias,
    )


def get_servicio_expiracion_password(
    session: SessionDep,
) -> ServicioExpiracionPassword:
    """AP-0037: servicio fail-safe del aviso de vencimiento, ligado a la peticion."""
    settings: Settings = get_settings()
    return ServicioExpiracionPassword(
        repo=SqlAlchemyPasswordExpiracionRepo(session),
        politica=get_politica_expiracion_password(),
        habilitado=settings.password_expiracion_aviso_enabled,
    )



def get_cambiar_password_expirada_uc(
    session: SessionDep, settings: SettingsDep
) -> CambiarPasswordExpiradaUseCase:
    """AP-0038: caso de uso del cambio autonomo de contrasena vencida en gracia."""
    return CambiarPasswordExpiradaUseCase(
        auth_service=get_auth_service(settings),
        usuario_repo=SQLAlchemyUsuarioRepo(session),
        modulos_repo=SQLAlchemyFrontendModulesRepo(session),
        expiracion=get_servicio_expiracion_password(session),
        throttle=get_login_throttle(),
        validador=get_validador_password(),
        bloqueo=get_servicio_bloqueo_cuenta(),
        bloqueo_duro=get_servicio_bloqueo_duro(),
        estado_credencial=get_estado_credencial_repo_sesion(session),
        sesiones=get_servicio_sesiones(get_settings()),
        historial=SqlAlchemyPasswordHistoryRepo(session),
        historial_tamano=settings.password_historial_tamano,
        historial_habilitado=settings.password_historial_habilitado,
    )


def get_politica_password_temporal() -> PoliticaPasswordTemporal:
    """AP-0048: politica de vigencia de la contrasena temporal (TTL con techo 120)."""
    settings: Settings = get_settings()
    return PoliticaPasswordTemporal(ttl_minutos=settings.password_temporal_ttl_minutos)


def get_servicio_password_temporal(session: SessionDep) -> ServicioPasswordTemporal:
    """AP-0046, AP-0047 y AP-0048: servicio de credenciales temporales (fail-safe)."""
    settings: Settings = get_settings()
    return ServicioPasswordTemporal(
        repo=SqlAlchemyPasswordTemporalRepo(session),
        politica=get_politica_password_temporal(),
        hasher=PasswordHasher(),
        habilitado=settings.password_temporal_habilitado,
        longitud=settings.password_temporal_longitud,
    )


def get_emitir_password_temporal_uc(
    session: SessionDep,
) -> EmitirPasswordTemporalUseCase:
    """AP-0047: caso de uso de emision de contrasena temporal por un tercero."""
    return EmitirPasswordTemporalUseCase(
        servicio=get_servicio_password_temporal(session),
        usuario_repo=SQLAlchemyUsuarioRepo(session),
        estado_credencial=get_estado_credencial_repo_sesion(session),
        sesiones=get_servicio_sesiones(get_settings()),
    )


def get_cambiar_password_temporal_uc(
    session: SessionDep, settings: SettingsDep
) -> CambiarPasswordTemporalUseCase:
    """AP-0046: caso de uso del cambio obligatorio de la contrasena temporal."""
    return CambiarPasswordTemporalUseCase(
        auth_service=get_auth_service(settings),
        usuario_repo=SQLAlchemyUsuarioRepo(session),
        modulos_repo=SQLAlchemyFrontendModulesRepo(session),
        servicio_temporal=get_servicio_password_temporal(session),
        expiracion=get_servicio_expiracion_password(session),
        throttle=get_login_throttle(),
        validador=get_validador_password(),
        bloqueo=get_servicio_bloqueo_cuenta(),
        bloqueo_duro=get_servicio_bloqueo_duro(),
        estado_credencial=get_estado_credencial_repo_sesion(session),
        sesiones=get_servicio_sesiones(get_settings()),
        historial=SqlAlchemyPasswordHistoryRepo(session),
        historial_tamano=settings.password_historial_tamano,
        historial_habilitado=settings.password_historial_habilitado,
    )


@lru_cache
def get_bloqueo_cuenta_repo() -> InMemoryBloqueoCuentaRepo:
    """AP-0009: estado de bloqueo de cuentas en memoria, singleton de proceso."""
    return InMemoryBloqueoCuentaRepo()


@lru_cache
def get_servicio_bloqueo_cuenta() -> ServicioBloqueoCuenta:
    """AP-0009: servicio de bloqueo de cuenta configurado por entorno."""
    settings: Settings = get_settings()
    return ServicioBloqueoCuenta(
        repo=get_bloqueo_cuenta_repo(),
        enabled=settings.lockout_enabled,
        max_intentos=settings.lockout_max_failed_attempts,
        duracion_minutos=settings.lockout_duration_minutes,
        auto_unlock=settings.lockout_auto_unlock_enabled,
        reset_on_success=settings.lockout_reset_counter_on_success,
        count_non_existing=settings.lockout_count_non_existing_users,
    )


@lru_cache
def get_bloqueo_duro_repo() -> InMemoryBloqueoDuroRepo:
    """AP-0157: estado de bloqueo duro en memoria, singleton de proceso."""
    return InMemoryBloqueoDuroRepo()


@lru_cache
def get_servicio_bloqueo_duro() -> ServicioBloqueoDuro:
    """AP-0157: servicio de bloqueo duro (administrativo/seguridad) de cuentas."""
    return ServicioBloqueoDuro(repo=get_bloqueo_duro_repo())


@lru_cache
def get_estado_credencial_repo() -> InMemoryEstadoCredencialRepo:
    """AP-0021: token_version por usuario en memoria, singleton de proceso."""
    return InMemoryEstadoCredencialRepo()


@lru_cache
def get_revocacion_token_store() -> InMemoryRevocacionTokenStore:
    """AP-0021: denylist de jti en memoria, singleton de proceso."""
    return InMemoryRevocacionTokenStore()


def get_estado_credencial_repo_sesion(
    session: AsyncSession | None,
) -> EstadoCredencialRepository:
    """AP-0049: token_version durable (tabla user_token_version) cuando la
    persistencia SQL esta activa; en su defecto, el singleton en memoria."""
    if get_settings().sesion_persistencia_sql and session is not None:
        return SQLAlchemyEstadoCredencialRepo(session)
    return get_estado_credencial_repo()


def get_revocacion_token_store_sesion(
    session: AsyncSession | None,
) -> RevocacionTokenStore:
    """AP-0049: denylist de jti durable (tabla revoked_token) cuando la
    persistencia SQL esta activa; en su defecto, el singleton en memoria."""
    if get_settings().sesion_persistencia_sql and session is not None:
        return SQLAlchemyRevocacionTokenRepo(session)
    return get_revocacion_token_store()


@lru_cache
def get_sesion_repo() -> InMemorySesionRepo:
    """AP-0130: Session Registry en memoria, singleton de proceso (Quick Win). En
    produccion multi-instancia se sustituye por un adaptador Redis/SQL (AP-0081) sin
    cambiar la firma del puerto SesionRepository."""
    return InMemorySesionRepo()


def get_politica_sesiones(settings: Settings) -> PoliticaSesiones:
    """AP-0130 (Opcion D): politica de sesiones concurrentes parametrizable por rol y
    canal. Maximo en 0 = ilimitado (modo 'informar')."""
    roles_canal: frozenset[str] = frozenset(
        r.strip() for r in settings.sesiones_roles_canal.split(",") if r.strip()
    )
    return PoliticaSesiones(
        max_canal=settings.sesiones_max_canal,
        max_otras=settings.sesiones_max_otras,
        roles_canal=roles_canal,
    )


def get_servicio_sesiones(settings: SettingsDep) -> ServicioSesiones:
    """AP-0130: informa y controla las sesiones concurrentes (Session Registry)."""
    return ServicioSesiones(
        repo=get_sesion_repo(),
        politica=get_politica_sesiones(settings),
        habilitado=settings.sesiones_concurrentes_enabled,
    )


def get_validador_sesion(session: AsyncSession | None = None) -> ValidadorSesion:
    """AP-0021 y AP-0049: validador de sesion por peticion (bloqueo + estado vivo
    del usuario + token_version + denylist). AP-0130: tambien rechaza sesiones
    revocadas desde otro dispositivo o expulsadas por limite de concurrencia."""
    return ValidadorSesion(
        estado_repo=get_estado_credencial_repo_sesion(session),
        denylist=get_revocacion_token_store_sesion(session),
        bloqueo=get_servicio_bloqueo_cuenta(),
        usuario_repo=SQLAlchemyUsuarioRepo(session) if session is not None else None,
        sesiones=get_servicio_sesiones(get_settings()),
    )


def get_servicio_alerta_seguridad(settings: Settings) -> ServicioAlertaSeguridad:
    """AP-0134: arma el alertador con los canales configurados (correo AP-0088 o webhook
    de Teams o Slack). Si no hay ninguno, usa el canal de log (siempre disponible)."""
    notificadores: list[NotificadorEventoSeguridad] = []
    if settings.alertas_seguridad_correo_destino:
        notificadores.append(
            NotificadorCorreoAlerta(
                get_notificador_correo(), settings.alertas_seguridad_correo_destino
            )
        )
    if settings.alertas_seguridad_webhook_url:
        notificadores.append(NotificadorWebhook(settings.alertas_seguridad_webhook_url))
    if not notificadores:
        notificadores.append(NotificadorLogAlerta())
    return ServicioAlertaSeguridad(
        notificadores=notificadores,
        umbral=SeveridadSeguridad(settings.alertas_seguridad_umbral),
        habilitado=settings.alertas_seguridad_enabled,
        dedup_ventana_seg=settings.alertas_seguridad_dedup_seg,
    )


def conectar_alerta_handler(settings: Settings) -> None:
    """AP-0134: engancha el AlertaHandler al logger de seguridad (idempotente)."""
    import logging

    logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)
    if any(isinstance(manejador, AlertaHandler) for manejador in logger.handlers):
        return
    handler: AlertaHandler = AlertaHandler(get_servicio_alerta_seguridad(settings))
    handler.setLevel(logging.WARNING)
    logger.addHandler(handler)


@lru_cache
def get_proveedor_clave_oidc() -> ProveedorClaveOidcEs256:
    """AP-0010: proveedor de clave de firma OIDC (ES256), singleton de proceso."""
    settings: Settings = get_settings()
    pem: bytes | None = (
        base64.b64decode(settings.oidc_signing_key_pem)
        if settings.oidc_signing_key_pem
        else None
    )
    return ProveedorClaveOidcEs256(pem)


def get_validador_token_estandar() -> ValidadorTokenEstandar:
    """AP-0010: validador de tokens estandar OIDC (firma JWKS, iss, aud, exp)."""
    settings: Settings = get_settings()
    return ValidadorTokenEstandar(
        proveedor=get_proveedor_clave_oidc(),
        issuer=settings.oidc_issuer,
        audiencia=settings.oidc_audience,
    )


def get_emitir_token_oidc_uc() -> EmitirTokenOidcUseCase:
    """AP-0010: caso de uso que emite tokens estandar OIDC/OAuth2."""
    settings: Settings = get_settings()
    return EmitirTokenOidcUseCase(
        proveedor=get_proveedor_clave_oidc(),
        issuer=settings.oidc_issuer,
        audiencia=settings.oidc_audience,
        ttl_segundos=settings.oidc_token_ttl_seg,
        scope_default=settings.oidc_scope_default,
    )


@lru_cache
def get_desafio_otp_store() -> InMemoryDesafioOtpStore:
    """AP-0012: almacen de desafios OTP de login en memoria, singleton de proceso."""
    settings: Settings = get_settings()
    return InMemoryDesafioOtpStore(ttl_segundos=settings.otp_login_codigo_ttl_seg)


@lru_cache
def get_servicio_otp_login() -> ServicioOtpLogin:
    """AP-0012: servicio de segundo factor OTP en el login."""
    settings: Settings = get_settings()
    roles: frozenset[str] = frozenset(
        r.strip().lower()
        for r in settings.otp_login_roles_criticos.split(",")
        if r.strip()
    )
    return ServicioOtpLogin(
        desafio_store=get_desafio_otp_store(),
        notificador=get_notificador_correo(),
        roles_criticos=roles,
        max_intentos=settings.otp_login_max_intentos,
        ttl_segundos=settings.otp_login_codigo_ttl_seg,
        enabled=settings.otp_login_enabled,
    )


def get_completar_login_otp_uc(session: SessionDep) -> CompletarLoginOtpUseCase:
    """AP-0012: caso de uso que completa el login tras verificar el OTP."""
    settings: Settings = get_settings()
    return CompletarLoginOtpUseCase(
        otp=get_servicio_otp_login(),
        auth_service=get_auth_service(settings),
        usuario_repo=SQLAlchemyUsuarioRepo(session),
        modulos_repo=SQLAlchemyFrontendModulesRepo(session),
        estado_credencial=get_estado_credencial_repo_sesion(session),
    )


@lru_cache
def get_dispositivo_repo() -> InMemoryDispositivoRepo:
    """AP-0014: registro de dispositivos por usuario en memoria, singleton de proceso."""
    return InMemoryDispositivoRepo()


def get_servicio_dispositivo() -> ServicioDispositivo:
    """AP-0014: servicio de identificacion del equipo origen en autenticacion."""
    settings: Settings = get_settings()
    return ServicioDispositivo(
        repo=get_dispositivo_repo(), enabled=settings.device_fingerprint_enabled
    )


@lru_cache
def get_custodia_compartida() -> ShamirCustodiaCompartida:
    """AP-0015: mecanismo de reparto de secreto de Shamir, singleton de proceso."""
    return ShamirCustodiaCompartida()


@lru_cache
def get_servicio_custodia_compartida() -> ServicioCustodiaCompartida:
    """AP-0015: servicio de doble custodia de la KEK maestra."""
    settings: Settings = get_settings()
    return ServicioCustodiaCompartida(
        reparto=get_custodia_compartida(), umbral=settings.custodia_umbral
    )

def get_verificador_permisos_objeto() -> VerificadorPermisosObjeto:
    """AP-0061: verificador de arranque del minimo privilegio sobre objetos nuevos de
    BD. Autoevalua (via la fabrica de sesiones autonoma) que la cuenta de la app no
    herede EXECUTE de base de datos; fail-fast en staging y produccion, warning en dev y
    test; conmutable por `db_object_privilege_check_enabled`."""
    settings: Settings = get_settings()
    return VerificadorPermisosObjeto(
        sonda=SqlServerSondaPermisosObjeto(get_session_factory()),
        app_env=settings.app_env,
        habilitado=settings.db_object_privilege_check_enabled,
    )

def _http_get_pam(
    timeout: int, verificar_tls: bool
) -> Callable[[str, dict[str, str]], dict[str, object]]:
    """AP-0062: GET al proveedor de credenciales de la herramienta PAM sobre HTTPS (verifica
    TLS por defecto); devuelve el JSON. Se separa para mantener ClientePamHttp puro y testeable."""

    def _get(url: str, consulta: dict[str, str]) -> dict[str, object]:
        with httpx.Client(timeout=timeout, verify=verificar_tls) as cliente:
            respuesta: httpx.Response = cliente.get(url, params=consulta)
            respuesta.raise_for_status()
            datos: object = respuesta.json()
        return datos if isinstance(datos, dict) else {}

    return _get


def _recuperador_pam(settings: Settings) -> Callable[[str], str]:
    """AP-0062: recuperador de secretos desde la herramienta PAM corporativa. Si PAM_PROVIDER_URL
    esta configurada, usa ClientePamHttp (CyberArk CCP o AAM, Conjur, Key Vault) sobre HTTPS. Si
    no, falla-seguro para no operar con una credencial no custodiada. Solo resta configurar el
    endpoint y las credenciales cuando Infraestructura provisione PAM (ver AP-0062)."""
    base_url: str = settings.pam_provider_url
    if not base_url:

        def _sin_configurar(nombre: str) -> str:
            raise SecretoNoDisponible(
                "AP-0062: integracion con la herramienta PAM pendiente de configurar "
                f"(PAM_PROVIDER_URL vacio); secreto {nombre}"
            )

        return _sin_configurar

    cliente: ClientePamHttp = ClientePamHttp(
        base_url=base_url,
        app_id=settings.pam_app_id,
        safe=settings.pam_safe,
        campo_secreto=settings.pam_secret_field,
        http_get=_http_get_pam(settings.pam_timeout, settings.pam_verify_tls),
    )
    return cliente.recuperar


@lru_cache
def get_proveedor_secretos() -> ProveedorSecretos:
    """AP-0062: selecciona el proveedor de secretos. pam usa el broker corporativo; en otro
    caso, el proveedor de entorno (dev y test, valores ya cargados por Settings)."""
    settings: Settings = get_settings()
    if settings.secrets_provider == PROVEEDOR_SECRETOS_PAM:
        return ProveedorSecretosPam(
            recuperador=_recuperador_pam(settings),
            ttl_seg=settings.pam_ttl_seg,
        )
    return ProveedorSecretosEntorno(
        {
            SECRETO_DB_USER: settings.db_user,
            SECRETO_DB_PASSWORD: settings.db_password,
        }
    )


def get_resolvedor_credencial_bd() -> ResolvedorCredencialBd:
    """AP-0062: resuelve la URL de conexion a la BD. En modo pam obtiene la credencial del
    broker en runtime (tolera rotacion); en otro caso usa la URL directa de Settings."""
    settings: Settings = get_settings()
    return ResolvedorCredencialBd(
        modo=settings.secrets_provider,
        url_directa=settings.database_url,
        proveedor=get_proveedor_secretos(),
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        driver=settings.db_driver,
        nombre_usuario=SECRETO_DB_USER,
        nombre_password=SECRETO_DB_PASSWORD,
    )
