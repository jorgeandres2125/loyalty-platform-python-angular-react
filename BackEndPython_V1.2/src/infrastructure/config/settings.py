import base64
import logging
import os
import secrets
from pathlib import Path
from typing import Final, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from src.domain.value_objects.retencion_categoria import RetencionCategoria
from src.shared.constants.cifrado_config import (
    CAMPOS_CREDENCIALES_CIFRABLES,
    ENV_CONFIG_KEK,
)
from src.shared.constants.custodia import CUSTODIA_UMBRAL_DEFECTO
from src.shared.constants.fail_secure import (
    JWT_SECRET_EPHEMERAL_BYTES,
    USUARIOS_BD_PROHIBIDOS,
)
from src.shared.constants.kms import (
    KMS_PROVIDER_LOCAL,
    KMS_PROVIDERS_RESPALDADOS_HSM,
    KMS_PROVIDERS_VALIDOS,
)
from src.shared.constants.otp import OTP_TTL_MAXIMO_SEG
from src.shared.constants.pasarela_borde import HEADER_EDGE_GATEWAY_DEFECTO
from src.shared.constants.password_expiracion import (
    PASSWORD_AVISO_DIAS_DEFECTO,
    PASSWORD_GRACIA_DIAS_DEFECTO,
    PASSWORD_HISTORIAL_TAMANO_DEFECTO,
    PASSWORD_TIMEZONE_DEFECTO,
    PASSWORD_VIGENCIA_DIAS_DEFECTO,
)
from src.shared.constants.password_policy import PASSWORD_MIN_LONGITUD_USUARIO_SERVICIO
from src.shared.constants.password_temporal import (
    PASSWORD_TEMPORAL_LONGITUD_DEFECTO,
    PASSWORD_TEMPORAL_TTL_MINUTOS_DEFECTO,
    PASSWORD_TEMPORAL_TTL_MINUTOS_MAXIMO,
)
from src.shared.constants.rate_limit_policy import (
    RATE_LIMIT_POR_IP_AUTH,
    RATE_LIMIT_POR_IP_DEFECTO,
)
from src.shared.constants.retencion_log import (
    RETENCION_ADMINISTRACION_DIAS_DEFECTO,
    RETENCION_AUDITORIA_DIAS_DEFECTO,
    RETENCION_ERROR_DIAS_DEFECTO,
    RETENCION_MINIMA_DIAS,
    RETENCION_OPERACION_DIAS_DEFECTO,
    RETENCION_SEGURIDAD_DIAS_DEFECTO,
)
from src.shared.constants.session_policy import (
    IDLE_TIMEOUT_CANAL_MIN,
    IDLE_TIMEOUT_OTRAS_MIN,
    JWT_EXPIRE_MINUTES_DEFECTO,
    JWT_EXPIRE_MINUTES_MAXIMO,
)

# Read APP_ENV before class definition so pydantic-settings loads the right file.
# os.environ is only read here, inside config/settings.py (per arch rule §15).
_APP_ENV: Final[str] = os.environ.get("APP_ENV", "development")

# Anclar los .env a la raíz del proyecto (BackEndPython_V1.2/) para que la carga
# no dependa del CWD del proceso (Docker WORKDIR, IDE, scripts con cd, etc.).
# settings.py vive en  src/infrastructure/config/  → parents[3] = raíz del proyecto.
_PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_ENV_FILES: Final[tuple[str, ...]] = (
    str(_PROJECT_ROOT / f".env.{_APP_ENV}"),
    str(_PROJECT_ROOT / ".env"),
)


def _kek_desde_entorno() -> bytes | None:
    """AP-0092: clave maestra (KEK) en base64 desde el entorno o Key Vault.

    Vacia = sin credenciales cifradas (desarrollo en texto plano). Se lee en
    settings.py (regla 15: os.environ solo se consulta aqui).
    """
    bruto: str = os.environ.get(ENV_CONFIG_KEK, "")
    if not bruto:
        return None
    return base64.b64decode(bruto)


class Settings(BaseSettings):
    # ── Entorno ──────────────────────────────────────────────────────────────
    app_env: str = _APP_ENV
    debug: bool = False

    # ── Base de datos ─────────────────────────────────────────────────────────
    db_host: str = "127.0.0.1"
    db_port: int = 1433
    db_name: str = "sufiatulado"
    # AP-0109: sin usuario de BD por defecto en el codigo (no 'sa'). dev/test
    # lo definen en su .env; staging/produccion lo exige el validador fail-secure.
    db_user: str = ""
    db_password: str = ""
    db_driver: str = "ODBC Driver 17 for SQL Server"
    # AP-0056: verificacion en arranque de que el principal de BD no pertenece a roles
    # privilegiados (sysadmin, db_owner, db_securityadmin, db_accessadmin, db_ddladmin).
    # Fail-fast en staging y produccion; deshabilitado en dev y test para no acoplar la
    # suite a la BD (la cuenta de minimo privilegio ya se garantiza por configuracion).
    db_privilege_check_enabled: bool = True

    # AP-0061: verificacion de minimo privilegio sobre objetos nuevos de BD (que la
    # cuenta de la app no herede EXECUTE de base de datos, alcanzando a todo
    # procedimiento o funcion futuro). Conmutable; fail-fast en staging y produccion.
    db_object_privilege_check_enabled: bool = True

    # AP-0062: origen de los secretos de la aplicacion. env (por defecto) los toma de las
    # variables de entorno inyectadas (Key Vault, Kubernetes); pam los obtiene en runtime
    # del proveedor de credenciales de la herramienta PAM corporativa, tolerando rotacion.
    # La integracion con PAM es un control corporativo (ver AP-0062).
    secrets_provider: str = "env"
    pam_provider_url: str = ""
    pam_app_id: str = ""
    pam_safe: str = ""
    pam_ttl_seg: int = Field(default=300, ge=30, le=3600)
    # AP-0062: parametros del cliente HTTP del proveedor de credenciales PAM.
    pam_secret_field: str = "Content"
    pam_timeout: int = Field(default=10, ge=1, le=120)
    pam_verify_tls: bool = True

    # AP-0064: la app solo se consume a traves del intermediario seguro (WAF, proxy,
    # gateway). Compensatorio de capa 7; deshabilitado por defecto hasta que Infra inyecte
    # la cabecera de borde. En staging y produccion, si se habilita, el secreto es obligatorio.
    edge_enforcement_enabled: bool = False
    edge_gateway_secret: str = ""
    edge_gateway_header: str = HEADER_EDGE_GATEWAY_DEFECTO

    # AP-0081: almacen efimero compartido entre replicas para alta disponibilidad.
    # Vacio -> adaptador en memoria (un solo proceso, dev/test). Con una URL redis://
    # se usa el adaptador Redis, que comparte OTP/OOB/throttle entre todas las replicas.
    redis_url: str = ""

    # AP-0120: verificacion de integridad de archivos criticos de la app al arranque (FIM).
    # Reporta el resultado en la bitacora de seguridad. Sin baseline configurado no hace nada.
    integridad_check_enabled: bool = True
    integridad_baseline_path: str = ""
    integridad_base_dir: str = "/app"

    # AP-0129: cierre de sesion por inactividad (idle). Canales 7 min, otras apps 20 min.
    # El tipo se determina por los roles (idle_roles_canal). Coexiste con el timeout
    # absoluto (AP-0162, jwt_expire_minutes): vence el que ocurra primero.
    idle_timeout_enabled: bool = True
    idle_timeout_canal_min: int = Field(default=IDLE_TIMEOUT_CANAL_MIN, ge=1, le=60)
    idle_timeout_otras_min: int = Field(default=IDLE_TIMEOUT_OTRAS_MIN, ge=1, le=120)
    idle_roles_canal: str = (
        "comisionista,comisionista consumo,ejecutivo,"
        "asesor logistico,asesor comercial,asesor callcenter"
    )

    # AP-0130: sesiones concurrentes. Modo por defecto informar (max en 0 = ilimitado):
    # se registran y se pueden listar o cerrar, sin expulsion. Un maximo mayor que 0
    # activa el control (Opcion D): al superarlo se expulsa la sesion mas antigua.
    sesiones_concurrentes_enabled: bool = True
    sesiones_max_canal: int = Field(default=0, ge=0, le=20)
    sesiones_max_otras: int = Field(default=0, ge=0, le=20)
    sesiones_roles_canal: str = (
        "comisionista,comisionista consumo,ejecutivo,"
        "asesor logistico,asesor comercial,asesor callcenter"
    )

    # Connection pool — mín 10, máx 100 (pool_size + max_overflow = 100)
    db_pool_min: int = Field(default=10,  ge=1,   le=100)   # pool_size
    db_pool_max: int = Field(default=100, ge=10,  le=500)   # pool_size + max_overflow
    db_pool_timeout: int = Field(default=30,  ge=5,  le=120)
    db_pool_recycle: int = Field(default=3600, ge=60, le=86400)

    # ── JWT ───────────────────────────────────────────────────────────────────
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = Field(
        default=JWT_EXPIRE_MINUTES_DEFECTO, ge=5, le=JWT_EXPIRE_MINUTES_MAXIMO
    )

    # ── SAPIN — keys en base64; vacías = crypto deshabilitado ─────────────────
    sapin_aes_key_ctr: str = ""
    sapin_aes_iv_ctr: str = ""
    sapin_aes_key_cbc: str = ""
    sapin_url: str = ""

    # AP-0075: versionamiento del token SAPIN. v1 = AES-128-CTR (contrato byte-a-byte con
    # MSP, legacy). v2 = AES-256-GCM (estandar corporativo). Emision conmutable; v2 exige la
    # clave de 32 bytes. Converger a v2 requiere coordinacion con MSP (dependencia externa).
    sapin_token_version: str = "v1"
    sapin_aes_key_gcm: str = ""

    # ── Cifrado de campos restringidos (Medida C — AP-0147 / AP-0095) ─────────
    # Clave AES-256 en base64 (32 bytes). Vacía = cifrado deshabilitado.
    # En staging/producción se inyecta desde KMS / Key Vault (§15), nunca en repo.
    app_encryption_key: str = ""
    app_encryption_key_id: int = 1
    # Claves retiradas para descifrar datos antiguos durante una rotación.
    # Formato: "id:base64,id:base64" (p.ej. "1:AAA...==,2:BBB...==").
    app_encryption_keys_retired: str = ""

    # Custodia de la clave maestra -- HSM o KMS (AP-0180).
    # kms_provider: 'local' (sustituto de software, solo desarrollo y pruebas) o
    # 'aws' (KMS con CMK respaldada por HSM). En staging y produccion debe ser un
    # proveedor respaldado por HSM o KMS: el guard de abajo lo exige.
    kms_provider: str = KMS_PROVIDER_LOCAL
    kms_key_id: str = ""
    # KEK del KMS local (base64 32 bytes); solo desarrollo. Vacio = clave efimera.
    kms_local_master_key: str = ""
    # DEK del cifrado de campos envuelta por el KMS (base64). Vacio = se usa la
    # clave en claro app_encryption_key (ruta de desarrollo, sin envelope).
    app_encryption_key_wrapped: str = ""


    # ── SMTP / correo (AP-0004 — verificación de propiedad del correo) ─────────
    # smtp_host vacío = modo consola (ConsoleEmailNotifier): no envía correo real,
    # registra el código en el log. En staging/producción se inyecta el relay SMTP.
    smtp_host: str = ""
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "no-responder@suficontigo.com"
    smtp_starttls: bool = True
    smtp_timeout: int = Field(default=15, ge=1, le=120)

    # ── Gateway HTTP de correo ('email-send-on-demand') ───────────────────────
    # Flujo de dos pasos (login → token → send). Tiene prioridad sobre SMTP.
    # email_api_base_url vacío = no usar gateway (cae a SMTP o consola).
    # La URL base cambia por ambiente y se inyecta vía .env.<APP_ENV> / secrets.
    # Si se omite el esquema, se asume https:// (poner http:// explícito si aplica).
    email_api_base_url: str = ""
    email_api_username: str = ""
    email_api_password: str = ""
    email_api_customer: str = "CX"
    email_api_product: str = "email"
    email_api_channel: str = "email-channel-soketlabs"
    email_api_sender: str = "no-responder@suficontigo.com"
    email_api_validate_blacklist: bool = False
    email_api_timeout: int = Field(default=15, ge=1, le=120)
    # Verificación del certificado TLS del gateway. Mantener True salvo que el
    # endpoint use un certificado no validable (p.ej. DNS de ELB sin cert propio).
    email_api_verify_tls: bool = True

    # ── Frontend (para construir enlaces en los correos) ──────────────────────
    # Vacío = el correo no incluye enlace clicable (solo el código).
    frontend_base_url: str = ""

    # ── Política de verificación de correo (AP-0004) ───────────────────────────
    verif_codigo_ttl_horas: int = Field(default=24, ge=1, le=72)
    verif_codigo_max_intentos: int = Field(default=5, ge=1, le=10)
    verif_reenvio_cooldown_seg: int = Field(default=60, ge=0, le=3600)

    # ── Anti fuerza bruta de login (AP-0007) ───────────────────────────────────
    # Retraso incremental ante credenciales erróneas: paso × nº de fallos, con tope.
    # Defaults requeridos por AP-0007: 5 s por fallo, máximo 30 s.
    login_retraso_paso_seg: int = Field(default=5, ge=0, le=60)
    login_retraso_max_seg: int = Field(default=30, ge=0, le=300)
    # Ventana de acumulación: tras este tiempo sin fallos, el contador se reinicia.
    login_intentos_ttl_seg: int = Field(default=900, ge=1, le=86400)
    # Leer la IP real del cliente desde X-Forwarded-For (primer salto) cuando el
    # backend está tras un proxy de confianza (IIS/ELB). False = usar la IP directa
    # (request.client.host); evita confiar en una cabecera falsificable en local.
    # Compartido por AP-0007 (login) y AP-0019 (registro/reset).
    trust_proxy_headers: bool = False

    # AP-0009: bloqueo de cuenta por intentos fallidos (mapea las claves
    # security.account-lockout). Configurable por entorno (LOCKOUT_*);
    # deshabilitado deja el login como antes (solo AP-0007 y rate limiting).
    lockout_enabled: bool = True
    lockout_max_failed_attempts: int = Field(default=5, ge=1, le=50)
    lockout_duration_minutes: int = Field(default=15, ge=1, le=1440)
    lockout_auto_unlock_enabled: bool = True
    lockout_reset_counter_on_success: bool = True
    lockout_notify_user_on_lock: bool = False
    lockout_notify_admin_on_lock: bool = True
    lockout_count_non_existing_users: bool = False
    lockout_generic_error_message_enabled: bool = True

    # AP-0021: revalidacion de sesion por peticion (token_version + denylist + bloqueo).
    # Deshabilitado deja el login como antes (solo firma + exp del JWT).
    sesion_validacion_enabled: bool = True

    # AP-0134: alertamiento de eventos de seguridad sensibles. El AlertaHandler,
    # enganchado a sufi.seguridad, despacha una alerta cuando la severidad del evento
    # alcanza el umbral. Compensatorio del pipeline SIEM (funciona sin el).
    alertas_seguridad_enabled: bool = True
    alertas_seguridad_umbral: str = "alta"
    alertas_seguridad_correo_destino: str = ""
    alertas_seguridad_webhook_url: str = ""
    alertas_seguridad_dedup_seg: int = 60

    # AP-0049: persistencia durable (SQL) de la revocacion de sesiones
    # (token_version y denylist de jti). En staging y produccion se eleva
    # automaticamente a True (replicas y reinicios); en dev y test basta la
    # memoria de proceso.
    sesion_persistencia_sql: bool = False

    # AP-0010: SSO estandar OIDC/OAuth2. Emite y valida tokens estandar (ES256, JWKS).
    # Habilitado, require_token acepta tokens estandar ademas del JWT propio.
    oidc_enabled: bool = True
    oidc_issuer: str = "https://api.suficontigo.com"
    oidc_audience: str = "sufi-api"
    oidc_signing_key_pem: str = ""
    oidc_token_ttl_seg: int = Field(default=900, ge=60, le=3600)
    oidc_scope_default: str = "openid perfil roles"

    # AP-0012: OTP de un solo uso en el login (segundo factor) para roles criticos.
    otp_login_enabled: bool = True
    otp_login_roles_criticos: str = "administrator,webmaster,documentador"
    otp_login_codigo_ttl_seg: int = Field(default=OTP_TTL_MAXIMO_SEG, ge=30, le=OTP_TTL_MAXIMO_SEG)
    otp_login_max_intentos: int = Field(default=5, ge=1, le=10)

    # AP-0014: identificacion del equipo origen en autenticacion (device fingerprinting).
    device_fingerprint_enabled: bool = True

    # AP-0015: doble custodia de la KEK maestra (Shamir 2-of-N). Los shares los inyectan
    # custodios independientes; ninguno solo posee la KEK. Deshabilitado = KEK de un origen.
    custodia_doble_enabled: bool = False
    custodia_umbral: int = Field(default=CUSTODIA_UMBRAL_DEFECTO, ge=2, le=10)
    custodia_shares: str = ""

    # AP-0025: sella los eventos de seguridad con una cadena de hash (tamper-evidence)
    # en origen; el destino inmutable (SIEM y WORM) conserva los sellos.
    sellado_log_enabled: bool = True

    # AP-0026: retencion de logs por categoria (dias), configurable por entorno con un
    # piso regulatorio; la app declara la politica y la infraestructura la materializa.
    retencion_log_enabled: bool = True
    retencion_seguridad_dias: int = Field(
        default=RETENCION_SEGURIDAD_DIAS_DEFECTO, ge=RETENCION_MINIMA_DIAS
    )
    retencion_auditoria_dias: int = Field(
        default=RETENCION_AUDITORIA_DIAS_DEFECTO, ge=RETENCION_MINIMA_DIAS
    )
    retencion_administracion_dias: int = Field(
        default=RETENCION_ADMINISTRACION_DIAS_DEFECTO, ge=RETENCION_MINIMA_DIAS
    )
    retencion_operacion_dias: int = Field(
        default=RETENCION_OPERACION_DIAS_DEFECTO, ge=RETENCION_MINIMA_DIAS
    )
    retencion_error_dias: int = Field(
        default=RETENCION_ERROR_DIAS_DEFECTO, ge=RETENCION_MINIMA_DIAS
    )

    # ── Gating de humano por retrasos incrementales (AP-0019) ──────────────────
    # Throttle por acción+IP en endpoints públicos sensibles (registro, reset…).
    # Los primeros `free` intentos por ventana no aplican retraso; luego crece
    # `paso` por intento hasta `max`. El control acepta "CAPTCHA o retrasos".
    throttle_humano_free_intentos: int = Field(default=2, ge=0, le=20)
    throttle_humano_paso_seg: int = Field(default=5, ge=0, le=60)
    throttle_humano_max_seg: int = Field(default=30, ge=0, le=300)
    throttle_humano_ttl_seg: int = Field(default=900, ge=1, le=86400)

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: str = "INFO"
    log_format: str = "json"    # json | text

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
        ]
    )
    # Fallback por expresión regular: permite cualquier origen que la cumpla,
    # además de los listados en cors_origins. Pensado para no atar el desarrollo
    # a una IP de LAN fija (DHCP). Vacío = deshabilitado (recomendado en prod).
    cors_origin_regex: str = ""

    # ── Cookies de sesión (Medida A — Cookie HttpOnly) ─────────────────────────
    # El JWT viaja en una cookie HttpOnly (inaccesible a JS → mitiga XSS, AP-0093/0099).
    cookie_auth_name: str = "sufi_access_token"
    csrf_cookie_name: str = "sufi_csrf"
    csrf_header_name: str = "X-CSRF-Token"
    cookie_secure: bool = True            # la cookie solo viaja por HTTPS (AP-0065)
    cookie_samesite: str = "lax"          # lax | strict | none
    cookie_domain: str = ""               # vacío = host-only (dev); .suficontigo.com en prod
    # AP-0128: exige X-CSRF-Token en peticiones autenticadas por cookie.
    csrf_enabled: bool = True

    # ── Cabeceras de seguridad / HTTPS (Medida B) ──────────────────────────────
    hsts_enabled: bool = True             # cabecera HSTS sobre HTTPS (AP-0200)
    hsts_max_age: int = 31536000

    # ── Compresión de respuestas (AP-0035) ─────────────────────────────────────
    # Comprime el cuerpo transferido al cliente negociando por Accept-Encoding
    # (zstd → brotli → gzip). No comprime cuerpos por debajo del umbral mínimo
    # (evita el overhead en respuestas diminutas).
    compress_enabled: bool = True
    compress_minimum_size: int = Field(default=500, ge=0, le=65536)

    # ── TLS local (uvicorn) — rutas a los certificados; vacío = HTTP plano ──────
    ssl_certfile: str = ""
    ssl_keyfile: str = ""

    # Almacenamiento de documentos (AP-0084): ruta absoluta configurable; vacio
    # = uploads/documentos anclado a la raiz del proyecto. Acceso solo via API.
    documentos_dir: str = ""

    # AP-0137: tamano maximo de archivos subidos por el usuario (bytes).
    # 10 MB por defecto; configurable por MAX_UPLOAD_BYTES. Se valida en el
    # endpoint de upload (rechazo 413).
    max_upload_bytes: int = Field(default=10_485_760, ge=1024, le=104_857_600)

    # AP-0144: verificacion de sincronizacion con la hora oficial del pais.
    hora_oficial_url: str = "https://aisenseapi.com/services/v1/datetime/-0500"
    hora_drift_max_seg: int = Field(default=60, ge=1, le=3600)
    hora_sync_timeout: int = Field(default=5, ge=1, le=60)
    hora_sync_enabled: bool = True

    # AP-0146: front de autenticacion propio (IdP estilo OAuth) para terceros.
    oauth_issuer: str = "sufi-auth"
    oauth_audiencias_permitidas: list[str] = Field(default_factory=lambda: ["sapin"])
    oauth_token_expire_minutes: int = Field(default=15, ge=1, le=120)
    oauth_scope_default: str = "perfil incentivos"

    # AP-0166: rate limiting por IP configurable en .env.
    rate_limit_enabled: bool = True
    rate_limit_por_ip_defecto: str = RATE_LIMIT_POR_IP_DEFECTO
    rate_limit_por_ip_auth: str = RATE_LIMIT_POR_IP_AUTH

    # AP-0003: autenticacion mutua TLS por certificado de cliente. El edge valida
    # el certificado y propaga la identidad; la app la mapea a un principal.
    # Deshabilitado por defecto (dev); se activa por entorno donde exista edge mTLS.
    mtls_enabled: bool = False
    # Secreto compartido que el edge anade para probar que las cabeceras de
    # identidad son suyas (anti-suplantacion). Vacio = no se confia en ninguna.
    mtls_edge_secret: str = ""
    # Allow-list de certificados: "fingerprint|sistema|empresa;fingerprint|sistema|empresa".
    # En staging y produccion se inyecta como secreto (Key Vault o KMS), no en repo.
    mtls_registro_certificados: str = ""

    # AP-0052: restriccion de acceso administrativo a redes de gestion. Control
    # compensatorio de capa 7; la restriccion primaria es de red (NSG, VPN, etc.).
    # Deshabilitado por defecto en dev y test; en staging y produccion el validador
    # lo eleva a obligatorio y exige CIDRs y secreto de edge (fail-fast).
    red_admin_enabled: bool = False
    # CIDRs de las redes de gestion autorizadas, separados por coma. Ejemplo:
    # "10.0.0.0/8,192.168.10.0/24". En staging y produccion se inyecta.
    red_admin_cidrs: str = ""
    # Secreto compartido que el edge anade para probar que la IP reenviada es suya.
    red_admin_edge_secret: str = ""
    # Cabecera de la que se toma la IP de cliente reenviada por el edge de confianza.
    red_admin_trusted_ip_header: str = "X-Forwarded-For"

    # AP-0053: modo de enforcement del RBAC por endpoint. "enforce" -> 403 al
    # faltar el permiso (deny-by-default); "audit" -> registra la denegacion y deja
    # pasar (canary de despliegue progresivo); "off" -> sin control. Los guardias
    # de administracion (AP-0001, catalogos) siempre fuerzan, sin importar el modo.
    authz_enforcement_mode: str = "enforce"

    # AP-0055: modo de autorizacion a nivel de objeto (BOLA/IDOR). Mismos valores y
    # semantica que authz_enforcement_mode; gobierna AuthorizationService.
    object_authz_mode: str = "enforce"

    # AP-0005: confirmacion fuera de banda (OOB) de transacciones criticas.
    # TTL del desafio (vencimiento, s) e intentos de codigo antes de bloquear.
    oob_codigo_ttl_seg: int = Field(default=OTP_TTL_MAXIMO_SEG, ge=30, le=OTP_TTL_MAXIMO_SEG)
    oob_max_intentos: int = Field(default=3, ge=1, le=10)

    # AP-0006: firma digital ES256. Clave privada PEM en base64; vacia = clave
    # efimera por proceso (solo desarrollo). En prod se inyecta o se usa KMS o HSM.
    firma_private_key_pem: str = ""

    # AP-0037: aviso de vencimiento de contrasena con 7 dias de antelacion.
    # habilitado=False apaga el aviso (login y sesion intactos). La vigencia define
    # cuando vence la contrasena desde su ultimo cambio; la ventana de aviso es
    # configurable para soportar futuras politicas. El servicio es fail-safe.
    password_expiracion_aviso_enabled: bool = True
    password_vigencia_dias: int = Field(
        default=PASSWORD_VIGENCIA_DIAS_DEFECTO, ge=1, le=3650
    )
    password_aviso_dias: int = Field(default=PASSWORD_AVISO_DIAS_DEFECTO, ge=1, le=90)

    # AP-0038: cambio autonomo de contrasena hasta N dias despues del vencimiento.
    # password_gracia_dias es la ventana de gracia (5 por defecto). El enforcement en
    # el login (bloquear sesion plena de credenciales vencidas y ofrecer el cambio
    # autonomo) es CONMUTABLE para un despliegue gradual: deshabilitado deja el login
    # como antes de AP-0038; el endpoint de cambio por vencimiento respeta siempre la
    # ventana de gracia. La clasificacion de estado es fail-open a VIGENTE.
    password_gracia_dias: int = Field(default=PASSWORD_GRACIA_DIAS_DEFECTO, ge=1, le=90)
    password_vencimiento_enforcement_enabled: bool = False

    # AP-0041: no reutilizar las ultimas N contrasenas. Se comparan con bcrypt (una por
    # una, en un hilo aparte). Tabla lateral user_password_history. Conmutable.
    password_historial_habilitado: bool = True
    password_historial_tamano: int = Field(
        default=PASSWORD_HISTORIAL_TAMANO_DEFECTO, ge=1, le=100
    )

    # AP-0043: un solo cambio de contrasena por dia (dia calendario en la zona de
    # negocio). password_timezone define la zona (America/Bogota, UTC-5, sin DST).
    password_max_un_cambio_por_dia: bool = True
    password_timezone: str = PASSWORD_TIMEZONE_DEFECTO

    # AP-0046, AP-0047 y AP-0048: contrasenas temporales. La temporal nunca emite
    # sesion plena: solo habilita el cambio obligatorio por el endpoint dedicado.
    # El TTL tiene techo normativo de 120 minutos (le=maximo): ningun entorno
    # puede superarlo. Conmutable: deshabilitado apaga la emision y la rama de
    # login (fail-safe), sin tocar la autenticacion normal.
    password_temporal_habilitado: bool = True
    password_temporal_ttl_minutos: int = Field(
        default=PASSWORD_TEMPORAL_TTL_MINUTOS_DEFECTO,
        ge=5,
        le=PASSWORD_TEMPORAL_TTL_MINUTOS_MAXIMO,
    )
    password_temporal_longitud: int = Field(
        default=PASSWORD_TEMPORAL_LONGITUD_DEFECTO, ge=12, le=64
    )

    # ── Propiedades derivadas ─────────────────────────────────────────────────
    @property
    def documentos_path(self) -> Path:
        """Ruta ABSOLUTA del directorio de documentos (AP-0084).

        Garantiza ruta absoluta sea cual sea el valor de `documentos_dir`
        (vacio, relativo o absoluto) y el CWD del proceso. Una ruta relativa
        se ancla a la raiz del proyecto.
        """
        base: Path = (
            Path(self.documentos_dir)
            if self.documentos_dir
            else _PROJECT_ROOT / "uploads" / "documentos"
        )
        if not base.is_absolute():
            base = _PROJECT_ROOT / base
        return base.resolve()

    @property
    def database_url(self) -> str:
        driver: str = self.db_driver.replace(" ", "+")
        return (
            f"mssql+aioodbc://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?driver={driver}&TrustServerCertificate=yes"
        )

    @property
    def db_max_overflow(self) -> int:
        """SQLAlchemy max_overflow = db_pool_max - db_pool_min."""
        return max(0, self.db_pool_max - self.db_pool_min)

    @model_validator(mode="after")
    def _persistencia_sesion_durable(self) -> "Settings":
        """AP-0049: en staging y produccion la revocacion de sesiones debe ser
        durable y compartida entre replicas; se eleva automaticamente a SQL."""
        entorno_superior: bool = self.app_env in ("staging", "production")
        if entorno_superior and not self.sesion_persistencia_sql:
            self.sesion_persistencia_sql = True
        return self

    @model_validator(mode="after")
    def _sesion_validacion_obligatoria(self) -> "Settings":
        """AP-0133: en staging y produccion la revalidacion de sesion por peticion
        (estado vivo del usuario, bloqueo y token_version) NO puede desactivarse: un
        usuario inhabilitado o bloqueado debe perder el acceso de inmediato."""
        if self.app_env in ("staging", "production") and not self.sesion_validacion_enabled:
            raise ValueError(
                "En staging y produccion SESION_VALIDACION_ENABLED debe ser True "
                "(AP-0133): la revalidacion de estado por peticion es obligatoria."
            )
        return self

    @model_validator(mode="after")
    def _alertamiento_obligatorio(self) -> "Settings":
        """AP-0134: en staging y produccion el alertamiento de eventos de seguridad NO
        puede desactivarse: todo evento sensible debe generar una alerta trazable."""
        if self.app_env in ("staging", "production") and not self.alertas_seguridad_enabled:
            raise ValueError(
                "En staging y produccion ALERTAS_SEGURIDAD_ENABLED debe ser True "
                "(AP-0134): el alertamiento de eventos de seguridad es obligatorio."
            )
        return self

    @model_validator(mode="after")
    def _red_admin_obligatoria(self) -> "Settings":
        """AP-0052: en staging y produccion el acceso administrativo debe
        restringirse a redes de gestion. Se eleva a habilitado y se exige la lista
        de CIDRs de gestion y el secreto de edge (fail-fast)."""
        if self.app_env not in ("staging", "production"):
            return self
        if not self.red_admin_enabled:
            self.red_admin_enabled = True
        if not self.red_admin_cidrs.strip():
            raise ValueError(
                f"En {self.app_env} se requiere RED_ADMIN_CIDRS (AP-0052): defina los "
                "segmentos de red de gestion autorizados."
            )
        if not self.red_admin_edge_secret:
            raise ValueError(
                f"En {self.app_env} se requiere RED_ADMIN_EDGE_SECRET (AP-0052) para "
                "confiar en la IP de cliente propagada por el edge."
            )
        return self

    @model_validator(mode="after")
    def _validar_authz_modo(self) -> "Settings":
        """AP-0053 / AP-0153: el modo de enforcement debe ser un valor conocido, y en
        staging y produccion DEBE ser 'enforce'. La autorizacion por permiso del lado
        del servidor no puede degradarse a solo-auditoria ni apagarse en un entorno
        real: seria depender del cliente para el control de acceso (Never Trust the
        Client)."""
        if self.authz_enforcement_mode not in ("enforce", "audit", "off"):
            raise ValueError(
                "AUTHZ_ENFORCEMENT_MODE invalido (AP-0053): "
                f"{self.authz_enforcement_mode}. Use enforce, audit u off."
            )
        entorno_real: bool = self.app_env in ("staging", "production")
        if entorno_real and self.authz_enforcement_mode != "enforce":
            raise ValueError(
                "En staging y produccion AUTHZ_ENFORCEMENT_MODE debe ser 'enforce' "
                "(AP-0153): la autorizacion por permiso en el servidor no puede "
                "degradarse a auditoria ni apagarse."
            )
        return self

    @model_validator(mode="after")
    def _validar_object_authz_modo(self) -> "Settings":
        """AP-0055 / AP-0153: el modo de autorizacion por objeto debe ser un valor
        conocido, y en staging y produccion DEBE ser 'enforce'. La autorizacion a nivel
        de objeto (BOLA/IDOR) no puede degradarse ni apagarse en un entorno real."""
        if self.object_authz_mode not in ("enforce", "audit", "off"):
            raise ValueError(
                "OBJECT_AUTHZ_MODE invalido (AP-0055): "
                f"{self.object_authz_mode}. Use enforce, audit u off."
            )
        entorno_real: bool = self.app_env in ("staging", "production")
        if entorno_real and self.object_authz_mode != "enforce":
            raise ValueError(
                "En staging y produccion OBJECT_AUTHZ_MODE debe ser 'enforce' "
                "(AP-0153): la autorizacion a nivel de objeto no puede degradarse ni "
                "apagarse."
            )
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def docs_habilitados(self) -> bool:
        """AP-0116: la documentacion interactiva (docs, redoc, openapi) solo
        se expone en desarrollo y test; en staging y produccion se deshabilita
        para no publicar la superficie del API (funcion innecesaria en prod).
        """
        return self.app_env in ("development", "test")

    # ──── Descifrado de credenciales del archivo de config (AP-0092) ────


    @model_validator(mode="after")
    def _validar_kms_clave_maestra(self) -> Self:
        # AP-0180: los procesos criptograficos criticos deben custodiar el KEK en un
        # HSM o KMS que no lo exponga durante su uso. El proveedor debe ser valido;
        # en staging y produccion debe estar respaldado por HSM o KMS (no 'local')
        # y declarar kms_key_id; de lo contrario el arranque falla (fail-fast).
        if self.kms_provider not in KMS_PROVIDERS_VALIDOS:
            raise ValueError(
                f"KMS_PROVIDER invalido (AP-0180): {self.kms_provider}. "
                f"Use uno de {sorted(KMS_PROVIDERS_VALIDOS)}."
            )
        if self.app_env not in ("staging", "production"):
            return self
        if self.kms_provider not in KMS_PROVIDERS_RESPALDADOS_HSM:
            raise ValueError(
                f"En {self.app_env} las claves criticas deben residir en un HSM o "
                f"KMS (AP-0180): configure KMS_PROVIDER respaldado por HSM, no "
                f"'{self.kms_provider}'."
            )
        if not self.kms_key_id:
            raise ValueError(
                f"En {self.app_env} se requiere KMS_KEY_ID para el proveedor "
                f"{self.kms_provider} (AP-0180)."
            )
        return self

    @model_validator(mode="after")
    def _descifrar_credenciales(self) -> Self:
        """AP-0092: descifra las credenciales marcadas con enc:gcm: en el
        archivo de configuracion usando la clave maestra (KEK).

        El texto plano solo vive en memoria; el .env guarda el criptograma.
        Un valor sin marcador pasa sin cambios (dev en texto plano). Debe
        ejecutarse antes que los validadores de longitud y placeholders.
        """
        from src.infrastructure.config.secret_decryptor import SecretDecryptor

        descifrador: SecretDecryptor = SecretDecryptor(_kek_desde_entorno())
        for nombre in CAMPOS_CREDENCIALES_CIFRABLES:
            valor: str = getattr(self, nombre)
            if descifrador.esta_cifrado(valor):
                setattr(self, nombre, descifrador.descifrar_valor(valor))
        return self

    # ── Política de contraseña de usuarios de servicio (AP-0044) ──────────────
    @model_validator(mode="after")
    def _validar_longitud_credenciales_servicio(self) -> Self:
        """Exige ≥20 caracteres en credenciales de conexión entre sistemas (AP-0044).

        Solo aplica en staging/producción: los defaults de desarrollo son
        intencionadamente débiles (Docker local) y no deben romper el arranque.
        Las credenciales vacías representan una integración deshabilitada y se
        omiten — solo se valida lo que efectivamente se usará para conectar.
        """
        if self.app_env not in ("staging", "production"):
            return self
        credenciales_servicio: dict[str, str] = {
            "jwt_secret_key": self.jwt_secret_key,
            "db_password": self.db_password,
            "smtp_password": self.smtp_password,
            "email_api_password": self.email_api_password,
        }
        cortas: list[str] = [
            nombre
            for nombre, valor in credenciales_servicio.items()
            if valor and len(valor) < PASSWORD_MIN_LONGITUD_USUARIO_SERVICIO
        ]
        if cortas:
            raise ValueError(
                "Credenciales de servicio con longitud insuficiente "
                f"(mínimo {PASSWORD_MIN_LONGITUD_USUARIO_SERVICIO} caracteres, AP-0044): "
                f"{', '.join(sorted(cortas))}"
            )
        return self

    @model_validator(mode="after")
    def _exigir_secretos_no_expuestos(self) -> Self:
        """AP-0079: ningun secreto puede quedar con un placeholder conocido y, en
        staging y produccion, los secretos criticos deben estar presentes.

        Los valores reales se inyectan por entorno (Key Vault o KMS); el codigo
        fuente nunca contiene un secreto utilizable por defecto.
        """
        placeholders: frozenset[str] = frozenset(
            {
                "CHANGE-ME-IN-PRODUCTION",
                "changeme",
                "change-me",
                "secret",
                "your-secret-key",
                "Admin123*",
            }
        )
        if self.jwt_secret_key and self.jwt_secret_key in placeholders:
            raise ValueError(
                "jwt_secret_key usa un placeholder inseguro (AP-0079): "
                "defina un secreto fuerte por entorno."
            )
        if self.app_env in ("staging", "production"):
            faltantes: list[str] = [
                nombre
                for nombre, valor in (
                    ("jwt_secret_key", self.jwt_secret_key),
                    ("db_password", self.db_password),
                )
                if not valor or valor in placeholders
            ]
            if faltantes:
                raise ValueError(
                    "Secretos ausentes o con placeholder en "
                    f"{self.app_env} (AP-0079): {', '.join(sorted(faltantes))}. "
                    "Inyecte los valores reales por entorno (Key Vault o KMS)."
                )
        return self

    # ──── Opciones por defecto seguras / fail-secure (AP-0109) ────
    @model_validator(mode="after")
    def _jwt_secret_fail_secure(self) -> Self:
        """AP-0109: nunca firmar JWT con una clave vacia.

        En desarrollo/test, si no se configuro jwt_secret_key, se genera una
        clave efimera fuerte por proceso: los tokens no sobreviven a un
        reinicio, pero jamas se firman con una clave vacia o adivinable. En
        staging/produccion la ausencia ya falla en _exigir_secretos_no_expuestos.
        """
        if not self.jwt_secret_key and self.app_env in ("development", "test"):
            self.jwt_secret_key = secrets.token_hex(JWT_SECRET_EPHEMERAL_BYTES)
            logging.getLogger("sufi.config").warning(
                "AP-0109: jwt_secret_key vacia en %s; se genero una clave "
                "efimera por proceso. Configure JWT_SECRET_KEY para tokens "
                "persistentes.",
                self.app_env,
            )
        return self

    @model_validator(mode="after")
    def _exigir_edge_secret(self) -> Self:
        """AP-0064: si el enforcement de borde esta habilitado en staging o produccion, el
        secreto de borde es obligatorio (fail-fast; evita bloquear todo el trafico por
        misconfig o dejar el control inerte)."""
        if not self.edge_enforcement_enabled:
            return self
        if self.app_env not in ("staging", "production"):
            return self
        if not self.edge_gateway_secret:
            raise ValueError(
                "EDGE_GATEWAY_SECRET es obligatorio en "
                f"{self.app_env} cuando EDGE_ENFORCEMENT_ENABLED=true (AP-0064)."
            )
        return self

    @model_validator(mode="after")
    def _exigir_db_user_seguro(self) -> Self:
        """AP-0109: en staging/produccion el usuario de BD debe estar definido
        y no ser una cuenta privilegiada ni un placeholder de plantilla.

        Fail-secure: nunca conectar como superadmin ('sa'/root/admin) por
        configuracion; se exige una cuenta de minimo privilegio explicita.
        """
        if self.app_env not in ("staging", "production"):
            return self
        usuario: str = self.db_user.strip().lower()
        if not usuario or usuario in USUARIOS_BD_PROHIBIDOS:
            raise ValueError(
                "db_user inseguro o ausente en "
                f"{self.app_env} (AP-0109): defina una cuenta de BD de minimo "
                "privilegio (no 'sa'/root/admin ni el placeholder de la plantilla)."
            )
        return self

    @model_validator(mode="after")
    def _validar_doble_custodia(self) -> Self:
        # AP-0015: en doble custodia se exige al menos `umbral` shares presentes
        # (fail-fast); ninguna persona sola puede reconstruir la KEK.
        if not self.custodia_doble_enabled:
            return self
        presentes: list[str] = [
            fragmento
            for fragmento in self.custodia_shares.split(",")
            if fragmento.strip()
        ]
        if len(presentes) < self.custodia_umbral:
            raise ValueError(
                "AP-0015 doble custodia habilitada: se requieren al menos "
                + str(self.custodia_umbral)
                + " shares en CUSTODIA_SHARES, hay "
                + str(len(presentes))
                + "."
            )
        return self

    def retencion_dias_por_categoria(self) -> dict[RetencionCategoria, int]:
        # AP-0026: fuente unica de los plazos por categoria que consumen el filtro de
        # logging y el endpoint de politica de retencion.
        return {
            RetencionCategoria.SEGURIDAD: self.retencion_seguridad_dias,
            RetencionCategoria.AUDITORIA: self.retencion_auditoria_dias,
            RetencionCategoria.ADMINISTRACION: self.retencion_administracion_dias,
            RetencionCategoria.OPERACION: self.retencion_operacion_dias,
            RetencionCategoria.ERROR: self.retencion_error_dias,
        }

    model_config = {
        "env_file": _ENV_FILES,
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }
