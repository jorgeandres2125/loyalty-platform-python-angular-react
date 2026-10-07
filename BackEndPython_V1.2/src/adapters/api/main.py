import os
import sys

# Garantiza que 'src/' esté en sys.path tanto en el proceso principal
# como en el subproceso hijo que uvicorn --reload lanza via multiprocessing.
_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _src not in sys.path:
    sys.path.insert(0, _src)

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette_compress import CompressMiddleware

from src.adapters.api.error_handlers import (
    acceso_no_autorizado_handler,
    audiencia_no_permitida_handler,
    email_invalido_handler,
    email_no_unico_handler,
    paso_omitido_handler,
    password_insegura_handler,
    rate_limit_excedido_handler,
    unhandled_exception_handler,
)
from src.adapters.api.middleware.contexto_seguridad_middleware import ContextoSeguridadMiddleware
from src.adapters.api.middleware.csrf_middleware import CSRFMiddleware
from src.adapters.api.middleware.metodos_http_middleware import MetodosHttpMiddleware
from src.adapters.api.middleware.mtls_identidad_middleware import MtlsIdentidadMiddleware
from src.adapters.api.middleware.parametros_duplicados_middleware import (
    ParametrosDuplicadosMiddleware,
)
from src.adapters.api.middleware.pasarela_borde_middleware import PasarelaBordeMiddleware
from src.adapters.api.middleware.red_administrativa_middleware import (
    RedAdministrativaMiddleware,
)
from src.adapters.api.middleware.security_audit_middleware import SecurityAuditMiddleware
from src.adapters.api.middleware.security_headers_middleware import SecurityHeadersMiddleware
from src.adapters.api.routers import (
    admin_afp_router,
    admin_arl_router,
    admin_asignaciones_router,
    admin_autorizaciones_router,
    admin_bancos_router,
    admin_ciudades_router,
    admin_departamentos_router,
    admin_eps_router,
    admin_profesiones_router,
    admin_programas_router,
    admin_subprogramas_router,
    admin_usuarios_router,
    asesor_consumo_router,
    asesor_movilidad_router,
    auditoria_router,
    auth_router,
    bloqueo_router,
    bloqueo_cuentas_router,
    canales_router,
    config_router,
    dashboard_router,
    debug_router,
    dispositivos_router,
    documentos_router,
    ejecutivos_router,
    firma_router,
    health_router,
    me_router,
    oauth_router,
    oficinas_router,
    oidc_router,
    oob_router,
    referencias_router,
    reportes_router,
    retencion_router,
    sapin_router,
    sesiones_router,
    ubicaciones_router,
    verificacion_cadena_router,
    verificacion_email_router,
)
from src.domain.exceptions.acceso_no_autorizado import AccesoNoAutorizado
from src.domain.exceptions.audiencia_no_permitida import AudienciaNoPermitida
from src.domain.exceptions.email_invalido import EmailInvalido
from src.domain.exceptions.email_no_unico import EmailNoUnico
from src.domain.exceptions.paso_omitido import PasoOmitido
from src.domain.exceptions.password_insegura import PasswordInsegura
from src.domain.value_objects.permiso import Permiso
from src.infrastructure.config.dependencies import require_token
from src.infrastructure.config.limiter import configurar_limites, limiter
from src.infrastructure.config.logging_config import configurar_logging
from src.infrastructure.config.permission_dependencies import require_permission
from src.infrastructure.config.settings import Settings
from src.infrastructure.persistence.database import dispose_engine, init_db
from src.infrastructure.security.registro_certificados_estatico import (
    RegistroCertificadosEstatico,
)
from src.shared.constants.mtls import RUTAS_MTLS_OBLIGATORIO
from src.shared.constants.pasarela_borde import RUTAS_EXENTAS_BORDE
from src.shared.constants.red_admin import RUTAS_ADMIN_RED


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    configurar_logging(
        settings.log_level,
        settings.log_format,
        settings.sellado_log_enabled,
        settings.retencion_dias_por_categoria() if settings.retencion_log_enabled else None,
    )
    # AP-0134: engancha el alertador de eventos de seguridad al logger sufi.seguridad.
    if settings.alertas_seguridad_enabled:
        from src.infrastructure.config.dependencies import conectar_alerta_handler

        conectar_alerta_handler(settings)
    from src.infrastructure.config.dependencies import get_resolvedor_credencial_bd
    _db_url: str = get_resolvedor_credencial_bd().url()  # AP-0062: broker PAM en modo pam
    init_db(
        _db_url,
        pool_size=settings.db_pool_min,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
        echo=settings.debug,
    )
    # AP-0056: verificacion de minimo privilegio del principal de BD (defensa en
    # profundidad sobre AP-0109). Fail-fast en staging y produccion si es privilegiado.
    from src.infrastructure.config.dependencies import (
        get_verificador_permisos_objeto,
        get_verificador_privilegio_bd,
    )

    await get_verificador_privilegio_bd().verificar()
    # AP-0061: verificacion de minimo privilegio sobre objetos nuevos (que la cuenta
    # de la app no herede EXECUTE de base de datos, alcanzando a todo proc y func).
    await get_verificador_permisos_objeto().verificar()
    # AP-0120: verificacion de integridad de los archivos criticos de la app al arranque,
    # reportada en la bitacora de seguridad. Fail-safe: nunca interrumpe el arranque.
    from src.infrastructure.config.dependencies import get_servicio_verificacion_integridad
    try:
        get_servicio_verificacion_integridad().ejecutar()
    except Exception:  # noqa: BLE001 -- el self-check de integridad no debe tumbar el arranque
        pass
    yield
    await dispose_engine()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    docs_habilitados: bool = settings.docs_habilitados
    app = FastAPI(
        title="SUFI Comisionistas API",
        version="1.2.0",
        description="Backend hexagonal para la plataforma SUFI — migración desde Drupal 7",
        lifespan=lifespan,
        docs_url="/docs" if docs_habilitados else None,
        redoc_url="/redoc" if docs_habilitados else None,
        openapi_url="/openapi.json" if docs_habilitados else None,
    )
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errores: list[str] = [
            f"{' → '.join(str(loc) for loc in error['loc'] if loc != 'body')}: {error['msg']}"
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=400,
            content={"detail": errores},
        )

    # AP-0119: handler global que evita filtrar stack traces, SQL o nombres
    # de tablas o base de datos en errores 500 no controlados.
    app.add_exception_handler(EmailInvalido, email_invalido_handler)
    app.add_exception_handler(EmailNoUnico, email_no_unico_handler)
    app.add_exception_handler(AudienciaNoPermitida, audiencia_no_permitida_handler)
    app.add_exception_handler(AccesoNoAutorizado, acceso_no_autorizado_handler)
    app.add_exception_handler(PasswordInsegura, password_insegura_handler)
    app.add_exception_handler(PasoOmitido, paso_omitido_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Protección CSRF para sesiones por cookie (Medida A — AP-0128).
    app.add_middleware(
        CSRFMiddleware,
        cookie_auth_name=settings.cookie_auth_name,
        csrf_cookie_name=settings.csrf_cookie_name,
        csrf_header_name=settings.csrf_header_name,
        enabled=settings.csrf_enabled,
    )

    # AP-0003: autenticacion mutua TLS. Exige certificado de cliente valido en las
    # rutas criticas (M2M y admin). Valida la identidad propagada por el edge contra
    # la allow-list y la mapea a un principal; sin certificado autorizado da 403.
    # Va por dentro de SecurityHeaders (su 403 recibe las cabeceras) y por dentro de
    # SecurityAudit y Contexto (queda auditado y correlacionado); por fuera de CSRF y
    # del enrutamiento (rechaza el certificado antes de tocar la logica de negocio).
    app.add_middleware(
        MtlsIdentidadMiddleware,
        registro=RegistroCertificadosEstatico.desde_config(settings.mtls_registro_certificados),
        rutas_obligatorias=RUTAS_MTLS_OBLIGATORIO,
        edge_secret=settings.mtls_edge_secret,
        enabled=settings.mtls_enabled,
    )

    # AP-0052: restringe el acceso administrativo a las redes de gestion. Control
    # compensatorio de capa 7 que complementa NSG, IP allow-list y VPN del
    # perimetro. Se ubica por dentro de SecurityHeaders y de SecurityAudit y
    # Contexto (su 403 recibe cabeceras y queda auditado y correlacionado) y por
    # fuera de mTLS (rechaza el origen de red antes de tocar cert y logica). Los
    # CIDRs y la cabecera de IP de confianza se configuran por entorno.
    _red_cidrs: tuple[str, ...] = tuple(
        c.strip() for c in settings.red_admin_cidrs.split(",") if c.strip()
    )
    app.add_middleware(
        RedAdministrativaMiddleware,
        cidrs_gestion=_red_cidrs,
        rutas_restringidas=RUTAS_ADMIN_RED,
        edge_secret=settings.red_admin_edge_secret,
        trusted_ip_header=settings.red_admin_trusted_ip_header,
        enabled=settings.red_admin_enabled,
    )
    # Cabeceras de seguridad / HSTS (Medida B — AP-0200/0201/0203/0204/0205).
    # AP-0064: consumo exclusivo a traves del intermediario seguro (WAF, proxy, gateway).
    # Compensatorio de capa 7: rechaza el trafico que no acredite haber pasado por el borde.
    app.add_middleware(
        PasarelaBordeMiddleware,
        edge_secret=settings.edge_gateway_secret,
        header=settings.edge_gateway_header,
        rutas_exentas=RUTAS_EXENTAS_BORDE,
        enabled=settings.edge_enforcement_enabled,
    )
    app.add_middleware(
        SecurityHeadersMiddleware,
        hsts_enabled=settings.hsts_enabled,
        hsts_max_age=settings.hsts_max_age,
    )
    # Auditoría de seguridad (AP-0022): registra acceso/excepciones de toda petición.
    # Va por fuera de CSRF/SecurityHeaders para capturar también sus respuestas (p.ej.
    # 403 de CSRF), pero por dentro de CORS para no auditar el preflight OPTIONS.
    app.add_middleware(SecurityAuditMiddleware, settings=settings)
    # Contexto de correlación (AP-0024): fija evento_id/usuario/ip/metodo/ruta en el
    # ContextVar antes de que SecurityAuditMiddleware emita logs, de modo que el
    # ContextoSeguridadFilter inyecta esos campos en cada LogRecord de la petición.
    app.add_middleware(ContextoSeguridadMiddleware, settings=settings)
    # Rate limiting por IP (AP-0166): SlowAPIMiddleware aplica el limite por
    # defecto a toda ruta sin limite propio; el login define su propio limite (mas
    # estricto) via decorador, que tiene prioridad. Configurable por .env (RATE_LIMIT_*).
    # Deshabilitado -> se apaga el limiter para no afectar la operacion ni las pruebas.
    if settings.rate_limit_enabled:
        configurar_limites(
            settings.rate_limit_por_ip_auth, settings.rate_limit_por_ip_defecto
        )
        limiter.enabled = True
        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)
        app.add_exception_handler(RateLimitExceeded, rate_limit_excedido_handler)
    else:
        limiter.enabled = False
    # Compresión de respuestas (AP-0035): negocia zstd → brotli → gzip según
    # Accept-Encoding y comprime el cuerpo ya formado por la app y el resto de
    # middlewares. Va por dentro de CORS (que sigue siendo el más externo) para no
    # alterar el preflight; sólo añade Content-Encoding / ajusta Content-Length.
    if settings.compress_enabled:
        app.add_middleware(
            CompressMiddleware,
            minimum_size=settings.compress_minimum_size,
        )
    # CORS último → middleware más externo (gestiona preflight antes que el resto).
    # Con cookies de credenciales NO se admite '*' como origen: se usan listas/regex
    # explícitas y allow_credentials=True (AP-0209).
    # AP-0185: rechaza metodos HTTP fuera del minimo soportado (TRACE, CONNECT, etc.)
    # con 405; va por dentro de CORS para no interferir con el preflight OPTIONS.
    # AP-0199: descarta parametros de query repetidos (HTTP Parameter Pollution),
    # conservando solo la primera aparicion de cada nombre no multi-valor. Normaliza
    # el query_string antes del enrutamiento, la auditoria y la validacion de entrada.
    app.add_middleware(ParametrosDuplicadosMiddleware)
    app.add_middleware(MetodosHttpMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=settings.cors_origin_regex or None,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", settings.csrf_header_name],
    )
    # auth y health son públicos; el resto requiere token JWT válido
    _secured = {"dependencies": [Depends(require_token)]}
    app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])
    # Público: verificación de propiedad del correo (doble opt-in, AP-0004). No
    # requiere JWT — el código enviado al correo es lo que prueba la identidad.
    app.include_router(
        verificacion_email_router.router,
        prefix="/api/v1/verificacion-email",
        tags=["verificacion-email"],
    )
    # AP-0137: limite de subida publico, referencia para el frontend.
    app.include_router(
        config_router.router,
        prefix="/api/v1/config",
        tags=["config"],
    )
    # AP-0144: monitoreo de sincronizacion horaria (publico).
    app.include_router(
        health_router.router,
        prefix="/api/v1/health",
        tags=["health"],
    )
    # AP-0146: IdP propio estilo OAuth para apps de terceros (requiere login).
    app.include_router(
        oauth_router.router,
        prefix="/api/v1/oauth",
        tags=["oauth"],
    )
    app.include_router(oidc_router.router, tags=["oidc"])
    app.include_router(dashboard_router.router, prefix="/api/v1/dashboard", tags=["dashboard"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.MOVILIDAD_ASESORES_GESTIONAR, Permiso.CONSUMO_ASESORES_GESTIONAR))])
    app.include_router(asesor_consumo_router.router, prefix="/api/v1/asesor-consumo", tags=["asesor-consumo"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.CONSUMO_ASESORES_GESTIONAR))])
    app.include_router(asesor_movilidad_router.router, prefix="/api/v1/asesor-movilidad", tags=["asesor-movilidad"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.MOVILIDAD_ASESORES_GESTIONAR))])
    app.include_router(me_router.router, prefix="/api/v1/me", tags=["me"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.MOVILIDAD_PERFIL_VER_PROPIO, Permiso.CONSUMO_PERFIL_VER_PROPIO))])
    app.include_router(auditoria_router.router, prefix="/api/v1/me", tags=["auditoria"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.AUDITORIA_VER_PROPIO))])
    app.include_router(dispositivos_router.router, prefix="/api/v1/me", tags=["dispositivos"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.DISPOSITIVOS_VER_PROPIO))])
    app.include_router(sesiones_router.router, prefix="/api/v1/me", tags=["sesiones"], dependencies=[Depends(require_token)])  # AP-0130: autoservicio puro (ownership por sub del token)
    app.include_router(oob_router.router, prefix="/api/v1/oob", tags=["oob"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.OOB_AUTORIZAR))])
    app.include_router(sapin_router.router, prefix="/api/v1/sapin", tags=["sapin"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.MOVILIDAD_PERFIL_VER_PROPIO, Permiso.CONSUMO_PERFIL_VER_PROPIO))])
    app.include_router(referencias_router.router, prefix="/api/v1/referencias", tags=["referencias"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_VER))])
    app.include_router(reportes_router.router, prefix="/api/v1/reportes", tags=["reportes"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.REPORTES_EXPORTAR))])
    app.include_router(documentos_router.router, prefix="/api/v1/documentos", tags=["documentos"], dependencies=[Depends(require_token)])
    app.include_router(ubicaciones_router.router, prefix="/api/v1/ubicaciones", tags=["ubicaciones"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_VER))])
    app.include_router(ejecutivos_router.router, prefix="/api/v1/ejecutivos", tags=["ejecutivos"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_GESTIONAR))])  # AP-0060: unificado bajo el permiso de administracion de catalogos
    app.include_router(firma_router.router, prefix="/api/v1/firmas", tags=["firmas"], dependencies=[Depends(require_token)])
    app.include_router(verificacion_cadena_router.router, prefix="/api/v1/admin/logs", tags=["admin-logs"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.ADMIN_CATALOGOS_GESTIONAR))])
    app.include_router(retencion_router.router, prefix="/api/v1/admin/logs", tags=["admin-logs"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.ADMIN_CATALOGOS_GESTIONAR))])
    app.include_router(bloqueo_router.router, prefix="/api/v1/admin/bloqueo", tags=["admin-bloqueo"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.USUARIOS_GESTIONAR_ESTADO))])
    app.include_router(bloqueo_cuentas_router.router, prefix="/api/v1/admin/cuentas", tags=["admin-cuentas"], dependencies=[Depends(require_token)])  # AP-0157: permisos por endpoint (softlock/hardlock)
    app.include_router(canales_router.router, prefix="/api/v1/canales", tags=["canales"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_VER))])
    app.include_router(oficinas_router.router, prefix="/api/v1/oficinas", tags=["oficinas"], dependencies=[Depends(require_token), Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_VER))])
    app.include_router(admin_usuarios_router.router, prefix="/api/v1/admin/usuarios", tags=["admin-usuarios"], **_secured)
    app.include_router(admin_afp_router.router, prefix="/api/v1/admin/afp", tags=["admin-afp"], **_secured)
    app.include_router(admin_arl_router.router, prefix="/api/v1/admin/arl", tags=["admin-arl"], **_secured)
    app.include_router(admin_eps_router.router, prefix="/api/v1/admin/eps", tags=["admin-eps"], **_secured)
    app.include_router(admin_bancos_router.router, prefix="/api/v1/admin/bancos", tags=["admin-bancos"], **_secured)
    app.include_router(admin_profesiones_router.router, prefix="/api/v1/admin/profesiones", tags=["admin-profesiones"], **_secured)
    app.include_router(admin_departamentos_router.router, prefix="/api/v1/admin/departamentos", tags=["admin-departamentos"], **_secured)
    app.include_router(admin_ciudades_router.router, prefix="/api/v1/admin/ciudades", tags=["admin-ciudades"], **_secured)
    app.include_router(admin_programas_router.router, prefix="/api/v1/admin/programas", tags=["admin-programas"], **_secured)
    app.include_router(admin_subprogramas_router.router, prefix="/api/v1/admin/subprogramas", tags=["admin-subprogramas"], **_secured)
    app.include_router(admin_autorizaciones_router.router, prefix="/api/v1/admin/autorizaciones", tags=["admin-autorizaciones"], **_secured)
    app.include_router(admin_asignaciones_router.router, prefix="/api/v1/admin/asignaciones", tags=["admin-asignaciones"], **_secured)

    # /debug solo se registra cuando debug=True (development/test). En staging/production
    # el router literalmente no se incluye, así que el endpoint no existe ni en OpenAPI.
    if settings.debug:
        app.include_router(debug_router.router, prefix="/api/v1/debug", tags=["debug"], **_secured)

    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok", "version": "1.2.0"}

    return app


app = create_app()
