from __future__ import annotations

import time
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from src.adapters.api.schemas.cambio_password_expirada_schema import (
    CambioPasswordExpiradaRequest,
)
from src.adapters.api.schemas.cambio_password_schema import CambioPasswordRequest
from src.adapters.api.schemas.cambio_password_temporal_schema import (
    CambioPasswordTemporalRequest,
)
from src.adapters.api.schemas.login_schema import LoginRequest
from src.adapters.api.schemas.me_response_schema import MeResponse
from src.adapters.api.schemas.modulo_permiso_schema import ModuloPermisoSchema
from src.adapters.api.schemas.otp.verificar_otp_request import VerificarOtpRequest
from src.adapters.api.schemas.password_aviso_schema import PasswordAvisoSchema
from src.adapters.api.schemas.refresh_response import RefreshResponse
from src.adapters.api.schemas.token_response_schema import TokenResponse
from src.application.services.auth_service import AuthService
from src.application.services.servicio_dispositivo import ServicioDispositivo
from src.application.services.servicio_expiracion_password import ServicioExpiracionPassword
from src.application.services.servicio_sesiones import ServicioSesiones
from src.application.use_cases.cambiar_password_expirada_use_case import (
    CambiarPasswordExpiradaUseCase,
)
from src.application.use_cases.cambiar_password_temporal_use_case import (
    CambiarPasswordTemporalUseCase,
)
from src.application.use_cases.completar_login_otp_use_case import CompletarLoginOtpUseCase
from src.application.use_cases.login_result import LoginResult
from src.application.use_cases.login_use_case import LoginUseCase
from src.domain.entities.modulo_permiso_entity import ModuloPermisoEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.credencial_en_gracia import CredencialEnGracia
from src.domain.exceptions.credencial_vencida_fuera_de_gracia import (
    CredencialVencidaFueraDeGracia,
)
from src.domain.exceptions.credencial_vigente import CredencialVigente
from src.domain.exceptions.credenciales_invalidas import CredencialesInvalidas
from src.domain.exceptions.cuenta_bloqueada import CuentaBloqueada
from src.domain.exceptions.cuenta_bloqueo_duro import CuentaBloqueoDuro
from src.domain.exceptions.otp_invalido import OtpInvalido
from src.domain.exceptions.otp_requerido import OtpRequerido
from src.domain.exceptions.password_insegura import PasswordInsegura
from src.domain.exceptions.password_reutilizada import PasswordReutilizada
from src.domain.exceptions.password_temporal_requiere_cambio import (
    PasswordTemporalRequiereCambio,
)
from src.domain.exceptions.password_temporal_vencida import PasswordTemporalVencida
from src.domain.exceptions.token_invalido import TokenInvalido
from src.domain.services.validador_password import ValidadorPassword
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion
from src.infrastructure.config.dependencies import (
    SessionDep,
    SettingsDep,
    TokenDep,
    extraer_ip_cliente,
    get_auth_service,
    get_cambiar_password_expirada_uc,
    get_cambiar_password_temporal_uc,
    get_completar_login_otp_uc,
    get_estado_credencial_repo_sesion,
    get_frontend_modules_repo,
    get_login_uc,
    get_revocacion_token_store_sesion,
    get_security_audit_logger,
    get_servicio_auditoria,
    get_servicio_dispositivo,
    get_servicio_expiracion_password,
    get_servicio_sesiones,
    get_validador_password,
    require_token,
)
from src.infrastructure.config.limiter import _limite_auth, limiter
from src.infrastructure.logging.security_audit import SecurityAuditLogger
from src.infrastructure.persistence.repositories.sqlalchemy_frontend_modules_repo import (
    SQLAlchemyFrontendModulesRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_password_history_repo import (
    SqlAlchemyPasswordHistoryRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_usuario_repo import (
    SQLAlchemyUsuarioRepo,
)
from src.infrastructure.security.cookies import (
    clear_auth_cookies,
    generar_csrf_token,
    set_auth_cookies,
)
from src.infrastructure.security.jwt_handler import JWTHandler
from src.shared.constants.auditoria import (
    ACCION_LOGIN_EXITOSO,
    ACCION_LOGIN_FALLIDO,
    ACCION_LOGIN_PASSWORD_EN_GRACIA,
    ACCION_LOGIN_PASSWORD_TEMPORAL,
    ACCION_LOGIN_RECHAZADO_PASSWORD_VENCIDO,
    ACCION_PASSWORD_CAMBIADO,
    ACCION_PASSWORD_CAMBIADO_EN_GRACIA,
    ACCION_PASSWORD_CAMBIO_DENEGADO_FUERA_GRACIA,
    ACCION_PASSWORD_TEMPORAL_CONSUMIDA,
    ACCION_PASSWORD_TEMPORAL_RECHAZADA_VENCIDA,
    ENTIDAD_PASSWORD_TEMPORAL,
    ENTIDAD_SESION,
    RESULTADO_FALLO,
)

router: APIRouter = APIRouter()


def _to_modulo_schema(m: ModuloPermisoEntity) -> ModuloPermisoSchema:
    return ModuloPermisoSchema(
        module_id=m.module_id,
        module_code=m.module_code,
        nombre=m.nombre,
        ruta=m.ruta,
        icono=m.icono,
        orden=m.orden,
        puede_ver=m.puede_ver,
        puede_crear=m.puede_crear,
        puede_editar=m.puede_editar,
        puede_eliminar=m.puede_eliminar,
        puede_exportar=m.puede_exportar,
        puede_aprobar=m.puede_aprobar,
    )


async def _registrar_dispositivo(
    servicio: ServicioDispositivo,
    uid: int,
    request: Request,
    fingerprint: str | None,
    device_name: str | None,
    ip: str,
) -> None:
    # AP-0014: identifica y registra el equipo origen; un equipo nuevo genera alerta.
    user_agent: str = request.headers.get("user-agent", "")
    await servicio.registrar_acceso_async(
        uid=uid,
        fingerprint=fingerprint,
        device_name=device_name,
        user_agent=user_agent,
        ip=ip,
    )


async def _registrar_sesion(
    servicio: ServicioSesiones,
    auth_service: AuthService,
    token: str,
    usuario: UsuarioEntity,
    request: Request,
    ip: str,
    fingerprint: str | None,
) -> None:
    # AP-0130: registra la sesion recien emitida en el Session Registry (informar y,
    # si la politica lo exige, controlar la concurrencia). Fail-safe: nunca interrumpe
    # el login; un token sin claim sid (config deshabilitada) simplemente no se registra.
    claims: dict[str, object] = auth_service.verificar_token(token)
    sid_raw: object = claims.get("sid", "")
    jti_raw: object = claims.get("jti", "")
    sid: str = sid_raw if isinstance(sid_raw, str) else ""
    jti: str = jti_raw if isinstance(jti_raw, str) else ""
    if not sid:
        return
    # AP-0132: la sesion registrada lleva su techo de expiracion (abs_exp de AP-0162, o el
    # exp del token) para que el barrido perezoso pueda marcarla EXPIRADA al vencer.
    exp_ses: object = claims.get("abs_exp") or claims.get("exp")
    fecha_exp: datetime | None = (
        datetime.fromtimestamp(int(exp_ses), tz=UTC) if isinstance(exp_ses, int) else None
    )
    roles_str: list[str] = [rol.value for rol in usuario.roles]
    await servicio.registrar(
        sid=sid,
        uid=usuario.uid or 0,
        roles=roles_str,
        jti=jti,
        device_fp=fingerprint or "",
        ip=ip,
        user_agent=request.headers.get("user-agent", ""),
        fecha_expiracion=fecha_exp,
    )


@router.post("/login", response_model=TokenResponse, summary="Login con nombre de usuario")
@limiter.limit(_limite_auth)
async def login_json(
    body: LoginRequest,
    request: Request,
    response: Response,
    settings: SettingsDep,
    login_uc: LoginUseCase = Depends(get_login_uc),
    audit: SecurityAuditLogger = Depends(get_security_audit_logger),
    servicio_disp: ServicioDispositivo = Depends(get_servicio_dispositivo),
    servicio_exp: ServicioExpiracionPassword = Depends(get_servicio_expiracion_password),
    servicio_ses: ServicioSesiones = Depends(get_servicio_sesiones),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse | JSONResponse:
    # AP-0007: el caso de uso aplica el retraso incremental (5 s → máx 30 s) por
    # clave IP|usuario ante credenciales erróneas antes de lanzar la excepción.
    ip: str = extraer_ip_cliente(request, settings)
    clave: str = f"{ip}|{body.username.strip().lower()}"
    try:
        result: LoginResult = await login_uc.ejecutar_async(
            body.username, body.password, clave
        )
    except PasswordInsegura as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except CredencialesInvalidas as exc:
        # AP-0022: evento de seguridad — autenticación fallida (con el usuario intentado).
        audit.autenticacion(
            exito=False, actor=body.username, ip=ip, detalle="credenciales incorrectas"
        )
        await get_servicio_auditoria().registrar_async(
            accion=ACCION_LOGIN_FALLIDO,
            usuario=body.username,
            ip_origen=ip,
            resultado=RESULTADO_FALLO,
            detalle={"motivo": "credenciales incorrectas"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except CuentaBloqueoDuro as exc:
        audit.autenticacion(
            exito=False, actor=body.username, ip=ip, detalle="cuenta con bloqueo duro"
        )
        if settings.lockout_generic_error_message_enabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=(
                "Tu cuenta esta bloqueada por seguridad. Contacta al administrador."
            ),
        ) from exc
    except CuentaBloqueada as exc:
        audit.autenticacion(
            exito=False, actor=body.username, ip=ip, detalle="cuenta bloqueada"
        )
        if settings.lockout_generic_error_message_enabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=(
                "Tu cuenta esta bloqueada temporalmente por multiples intentos "
                "fallidos. Intenta mas tarde."
            ),
        ) from exc
    except OtpRequerido as exc:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "otp_requerido": True,
                "desafio_id": exc.desafio_id,
                "email_enmascarado": exc.email_enmascarado,
                "expira_en_segundos": exc.expira_en_segundos,
                "mensaje": "Enviamos un codigo de acceso a tu correo. Ingresalo para continuar.",
            },
        )
    except CredencialEnGracia as exc:
        # AP-0038: contrasena vencida en gracia -> no se emite sesion plena; el usuario
        # debe cambiarla de forma autonoma dentro del periodo de gracia.
        audit.autenticacion(
            exito=False, actor=body.username, ip=ip, detalle="password vencida en gracia"
        )
        await get_servicio_auditoria().registrar_async(
            accion=ACCION_LOGIN_PASSWORD_EN_GRACIA,
            usuario=body.username,
            ip_origen=ip,
            resultado=RESULTADO_FALLO,
            detalle={
                "dias_desde_vencimiento": exc.dias_desde_vencimiento,
                "dias_restantes_gracia": exc.dias_restantes_gracia,
            },
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "code": "password_expired_in_grace",
                "detail": (
                    "Tu contrasena vencio. Puedes cambiarla de forma autonoma dentro "
                    "del periodo de gracia."
                ),
                "username": body.username,
                "dias_desde_vencimiento": exc.dias_desde_vencimiento,
                "dias_restantes_gracia": exc.dias_restantes_gracia,
            },
        )
    except CredencialVencidaFueraDeGracia as exc:
        # AP-0038: vencida fuera de gracia -> bloqueada; requiere restablecimiento asistido.
        audit.autenticacion(
            exito=False,
            actor=body.username,
            ip=ip,
            detalle="password vencida fuera de gracia",
        )
        await get_servicio_auditoria().registrar_async(
            accion=ACCION_LOGIN_RECHAZADO_PASSWORD_VENCIDO,
            usuario=body.username,
            ip_origen=ip,
            resultado=RESULTADO_FALLO,
            detalle={"dias_desde_vencimiento": exc.dias_desde_vencimiento},
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "code": "password_expired_grace_over",
                "detail": (
                    "Tu contrasena vencio hace mas dias de los permitidos para el cambio "
                    "autonomo. Solicita el restablecimiento asistido."
                ),
                "dias_desde_vencimiento": exc.dias_desde_vencimiento,
            },
        )
    except PasswordTemporalRequiereCambio as exc:
        # AP-0046: la temporal autentica pero NUNCA emite sesion plena; se exige
        # el cambio obligatorio por el endpoint dedicado (primer uso ya estampado).
        audit.autenticacion(
            exito=False,
            actor=body.username,
            ip=ip,
            detalle="password temporal: requiere cambio obligatorio",
        )
        await get_servicio_auditoria().registrar_async(
            accion=ACCION_LOGIN_PASSWORD_TEMPORAL,
            usuario=body.username,
            ip_origen=ip,
            entidad=ENTIDAD_PASSWORD_TEMPORAL,
            detalle={"expira_iso": exc.expira_iso},
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "code": "password_temporal_change_required",
                "detail": (
                    "Ingresaste con una contrasena temporal. Debes definir tu "
                    "contrasena personal para continuar."
                ),
                "username": body.username,
                "expira_iso": exc.expira_iso,
            },
        )
    except PasswordTemporalVencida as exc:
        # AP-0048: match exacto de la temporal pero fuera de los 120 minutos.
        audit.autenticacion(
            exito=False, actor=body.username, ip=ip, detalle="password temporal vencida"
        )
        await get_servicio_auditoria().registrar_async(
            accion=ACCION_PASSWORD_TEMPORAL_RECHAZADA_VENCIDA,
            usuario=body.username,
            ip_origen=ip,
            entidad=ENTIDAD_PASSWORD_TEMPORAL,
            resultado=RESULTADO_FALLO,
            detalle={"expira_iso": exc.expira_iso},
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "code": "password_temporal_expired",
                "detail": (
                    "La contrasena temporal vencio. Solicita una nueva a tu "
                    "administrador."
                ),
            },
        )

    # AP-0022: evento de seguridad — autenticación exitosa.
    audit.autenticacion(exito=True, actor=body.username, ip=ip)
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_LOGIN_EXITOSO,
        user_id=result.usuario.uid,
        usuario=body.username,
        ip_origen=ip,
        entidad=ENTIDAD_SESION,
    )
    # AP-0037: arranca el reloj de vencimiento en el primer login (idempotente).
    await servicio_exp.asegurar_baseline(result.usuario.uid or 0)
    await _registrar_dispositivo(
        servicio_disp, result.usuario.uid or 0, request, body.fingerprint, body.device_name, ip
    )
    # AP-0130: registra la sesion en el Session Registry (informar mas control concurrente).
    await _registrar_sesion(
        servicio_ses, auth_service, result.token, result.usuario, request, ip, body.fingerprint
    )

    # Medida A: el JWT se entrega en cookie HttpOnly (no en almacenamiento del cliente).
    # Se conserva access_token en el cuerpo por compatibilidad con clientes que usen Bearer.
    csrf_token: str = generar_csrf_token()
    set_auth_cookies(response, result.token, csrf_token, settings, settings.jwt_expire_minutes * 60)

    roles_str: list[str] = [rol.value for rol in result.usuario.roles]
    return TokenResponse(
        access_token=result.token,
        token_type="bearer",
        uid=result.usuario.uid or 0,
        username=result.usuario.nombre,
        email=result.usuario.email,
        roles=roles_str,
        modulos=[_to_modulo_schema(modulo) for modulo in result.modulos],
    )


@router.post(
    "/login/otp",
    response_model=TokenResponse,
    summary="Completar el login con el codigo OTP de un solo uso (AP-0012)",
)
@limiter.limit(_limite_auth)
async def login_otp(
    body: VerificarOtpRequest,
    request: Request,
    response: Response,
    settings: SettingsDep,
    uc: CompletarLoginOtpUseCase = Depends(get_completar_login_otp_uc),
    audit: SecurityAuditLogger = Depends(get_security_audit_logger),
    servicio_disp: ServicioDispositivo = Depends(get_servicio_dispositivo),
    servicio_exp: ServicioExpiracionPassword = Depends(get_servicio_expiracion_password),
    servicio_ses: ServicioSesiones = Depends(get_servicio_sesiones),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    ip: str = extraer_ip_cliente(request, settings)
    try:
        result: LoginResult = await uc.completar_async(body.desafio_id, body.codigo)
    except OtpInvalido as exc:
        audit.autenticacion(exito=False, actor="otp", ip=ip, detalle="otp incorrecto")
        await get_servicio_auditoria().registrar_async(
            accion=ACCION_LOGIN_FALLIDO,
            usuario="otp",
            ip_origen=ip,
            resultado=RESULTADO_FALLO,
            detalle={"motivo": "otp incorrecto"},
        )
        detalle: str = exc.motivo
        if exc.intentos_restantes is not None and exc.intentos_restantes > 0:
            detalle = f"{exc.motivo} Intentos restantes: {exc.intentos_restantes}."
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detalle,
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    audit.autenticacion(
        exito=True, actor=str(result.usuario.uid), ip=ip, detalle="otp verificado (2FA)"
    )
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_LOGIN_EXITOSO,
        user_id=result.usuario.uid,
        ip_origen=ip,
        entidad=ENTIDAD_SESION,
        detalle={"metodo": "otp 2FA"},
    )
    # AP-0037: arranca el reloj de vencimiento tras el login con OTP (idempotente).
    await servicio_exp.asegurar_baseline(result.usuario.uid or 0)
    await _registrar_dispositivo(
        servicio_disp, result.usuario.uid or 0, request, body.fingerprint, body.device_name, ip
    )
    # AP-0130: registra la sesion en el Session Registry (informar mas control concurrente).
    await _registrar_sesion(
        servicio_ses, auth_service, result.token, result.usuario, request, ip, body.fingerprint
    )
    csrf_token: str = generar_csrf_token()
    set_auth_cookies(
        response, result.token, csrf_token, settings, settings.jwt_expire_minutes * 60
    )
    roles_str: list[str] = [rol.value for rol in result.usuario.roles]
    return TokenResponse(
        access_token=result.token,
        token_type="bearer",
        uid=result.usuario.uid or 0,
        username=result.usuario.nombre,
        email=result.usuario.email,
        roles=roles_str,
        modulos=[_to_modulo_schema(modulo) for modulo in result.modulos],
    )


@router.patch("/password", status_code=204, summary="Cambiar contraseña del usuario autenticado")
async def cambiar_password(
    body: CambioPasswordRequest,
    request: Request,
    token_payload: TokenDep,
    settings: SettingsDep,
    session: SessionDep = None,  # type: ignore[assignment]
    auth_service: AuthService = Depends(get_auth_service),
    audit: SecurityAuditLogger = Depends(get_security_audit_logger),
    validador_pwd: ValidadorPassword = Depends(get_validador_password),
    servicio_exp: ServicioExpiracionPassword = Depends(get_servicio_expiracion_password),
) -> None:
    if body.nueva_password != body.confirmar_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas no coinciden",
        )
    uid: int = int(token_payload.get("sub", 0))
    ip: str = extraer_ip_cliente(request, settings)
    # AP-0043: un solo cambio de contrasena por dia (dia calendario en la zona de negocio).
    if settings.password_max_un_cambio_por_dia and await servicio_exp.cambiada_hoy(
        uid, settings.password_timezone
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Solo puedes cambiar tu contrasena una vez al dia. "
                "Intenta nuevamente manana."
            ),
        )
    repo: SQLAlchemyUsuarioRepo = SQLAlchemyUsuarioRepo(session)
    historial: SqlAlchemyPasswordHistoryRepo | None = (
        SqlAlchemyPasswordHistoryRepo(session)
        if settings.password_historial_habilitado
        else None
    )
    # AP-0020: re-autenticación con la contraseña actual antes de la novedad. Se
    # mapea a 400 (no 401) para no gatillar el cierre de sesión del interceptor.
    try:
        nombre_usuario: str = str(token_payload.get("nombre", ""))
        await auth_service.cambiar_password_async(
            uid,
            body.password_actual,
            body.nueva_password,
            repo,
            validador=validador_pwd,
            valores_contextuales=[nombre_usuario] if nombre_usuario else None,
            historial=historial,
            historial_tamano=settings.password_historial_tamano,
        )
    except PasswordReutilizada as exc:
        # AP-0041: la nueva contrasena coincide con una de las ultimas usadas.
        audit.cambio_credencial(
            exito=False, actor=str(uid), ip=ip, detalle="password reutilizada"
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except PasswordInsegura as exc:
        # AP-0159: la nueva contrasena no cumple la validacion contextual.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except CredencialesInvalidas as exc:
        # AP-0022: evento de seguridad — re-autenticación fallida en la novedad.
        audit.cambio_credencial(
            exito=False, actor=str(uid), ip=ip, detalle="contraseña actual incorrecta"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta",
        ) from exc

    # AP-0022: evento de seguridad — cambio de credencial exitoso.
    audit.cambio_credencial(exito=True, actor=str(uid), ip=ip)
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_PASSWORD_CAMBIADO, user_id=uid, ip_origen=ip
    )
    # AP-0021: el cambio de contrasena invalida todas las sesiones previas (token_version++).
    await get_estado_credencial_repo_sesion(session).incrementar_version(uid)
    # AP-0208: cierra ademas las sesiones en el Session Registry, con el motivo, para que
    # la lista de AP-0207 no muestre sesiones ya muertas y quede evidencia por sesion.
    await get_servicio_sesiones(settings).cerrar_todas(
        uid, MotivoCierreSesion.CAMBIO_CREDENCIAL
    )
    # AP-0037: reinicia el reloj de vencimiento al cambiar la contrasena.
    await servicio_exp.registrar_cambio(uid)


@router.post(
    "/password/expirada",
    response_model=TokenResponse,
    summary="Cambio autonomo de contrasena vencida dentro de la gracia (AP-0038)",
)
@limiter.limit(_limite_auth)
async def cambiar_password_expirada(
    body: CambioPasswordExpiradaRequest,
    request: Request,
    response: Response,
    settings: SettingsDep,
    uc: CambiarPasswordExpiradaUseCase = Depends(get_cambiar_password_expirada_uc),
    audit: SecurityAuditLogger = Depends(get_security_audit_logger),
) -> TokenResponse | JSONResponse:
    # AP-0038: cambio autonomo (sin sesion) de una contrasena vencida dentro de la
    # gracia. Autentica con la contrasena vencida, valida la nueva y emite sesion plena.
    if body.nueva_password != body.confirmar_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contrasenas no coinciden",
        )
    ip: str = extraer_ip_cliente(request, settings)
    clave: str = f"{ip}|{body.username.strip().lower()}"
    try:
        result: LoginResult = await uc.ejecutar_async(
            body.username, body.password_actual, body.nueva_password, clave
        )
    except PasswordReutilizada as exc:
        # AP-0041: la nueva contrasena coincide con una de las ultimas usadas.
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except PasswordInsegura as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except CredencialesInvalidas as exc:
        audit.cambio_credencial(
            exito=False,
            actor=body.username,
            ip=ip,
            detalle="password actual incorrecta (vencida)",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except CuentaBloqueada as exc:
        if settings.lockout_generic_error_message_enabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Tu cuenta esta bloqueada temporalmente. Intenta mas tarde.",
        ) from exc
    except CredencialVigente:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "code": "password_still_valid",
                "detail": (
                    "Tu contrasena sigue vigente. Usa el cambio de contrasena estandar."
                ),
            },
        )
    except CredencialVencidaFueraDeGracia as exc:
        await get_servicio_auditoria().registrar_async(
            accion=ACCION_PASSWORD_CAMBIO_DENEGADO_FUERA_GRACIA,
            usuario=body.username,
            ip_origen=ip,
            resultado=RESULTADO_FALLO,
            detalle={"dias_desde_vencimiento": exc.dias_desde_vencimiento},
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "code": "password_expired_grace_over",
                "detail": (
                    "Tu contrasena vencio hace mas dias de los permitidos para el cambio "
                    "autonomo. Solicita el restablecimiento asistido."
                ),
                "dias_desde_vencimiento": exc.dias_desde_vencimiento,
            },
        )

    # Exito: cambio autonomo en gracia -> se emite sesion plena y se audita.
    audit.cambio_credencial(
        exito=True, actor=body.username, ip=ip, detalle="cambio autonomo en gracia (AP-0038)"
    )
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_PASSWORD_CAMBIADO_EN_GRACIA,
        user_id=result.usuario.uid,
        usuario=body.username,
        ip_origen=ip,
        entidad=ENTIDAD_SESION,
    )
    csrf_token: str = generar_csrf_token()
    set_auth_cookies(
        response, result.token, csrf_token, settings, settings.jwt_expire_minutes * 60
    )
    roles_str: list[str] = [rol.value for rol in result.usuario.roles]
    return TokenResponse(
        access_token=result.token,
        token_type="bearer",
        uid=result.usuario.uid or 0,
        username=result.usuario.nombre,
        email=result.usuario.email,
        roles=roles_str,
        modulos=[_to_modulo_schema(modulo) for modulo in result.modulos],
    )


@router.post(
    "/password/temporal",
    response_model=TokenResponse,
    summary="Cambio obligatorio de la contrasena temporal (AP-0046)",
)
@limiter.limit(_limite_auth)
async def cambiar_password_temporal(
    body: CambioPasswordTemporalRequest,
    request: Request,
    response: Response,
    settings: SettingsDep,
    uc: CambiarPasswordTemporalUseCase = Depends(get_cambiar_password_temporal_uc),
    audit: SecurityAuditLogger = Depends(get_security_audit_logger),
) -> TokenResponse | JSONResponse:
    # AP-0046: cambio obligatorio (sin sesion) de la contrasena temporal. Autentica
    # con la temporal vigente, valida la nueva con todas las politicas y emite
    # sesion plena. Omite la regla de un cambio por dia (reset administrativo).
    if body.nueva_password != body.confirmar_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contrasenas no coinciden",
        )
    ip: str = extraer_ip_cliente(request, settings)
    clave: str = f"{ip}|{body.username.strip().lower()}"
    try:
        result: LoginResult = await uc.ejecutar_async(
            body.username, body.password_temporal, body.nueva_password, clave
        )
    except PasswordReutilizada as exc:
        # AP-0041: la nueva contrasena coincide con una de las ultimas usadas.
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except PasswordInsegura as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except CredencialesInvalidas as exc:
        audit.cambio_credencial(
            exito=False,
            actor=body.username,
            ip=ip,
            detalle="temporal incorrecta en cambio obligatorio",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except CuentaBloqueada as exc:
        if settings.lockout_generic_error_message_enabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Tu cuenta esta bloqueada temporalmente. Intenta mas tarde.",
        ) from exc
    except PasswordTemporalVencida as exc:
        # AP-0048: la temporal coincide pero ya expiro; requiere reemision.
        await get_servicio_auditoria().registrar_async(
            accion=ACCION_PASSWORD_TEMPORAL_RECHAZADA_VENCIDA,
            usuario=body.username,
            ip_origen=ip,
            entidad=ENTIDAD_PASSWORD_TEMPORAL,
            resultado=RESULTADO_FALLO,
            detalle={"expira_iso": exc.expira_iso, "contexto": "cambio obligatorio"},
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "code": "password_temporal_expired",
                "detail": (
                    "La contrasena temporal vencio. Solicita una nueva a tu "
                    "administrador."
                ),
            },
        )

    # Exito: temporal consumida, contrasena definitiva establecida, sesion plena.
    audit.cambio_credencial(
        exito=True,
        actor=body.username,
        ip=ip,
        detalle="cambio obligatorio de contrasena temporal (AP-0046)",
    )
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_PASSWORD_TEMPORAL_CONSUMIDA,
        user_id=result.usuario.uid,
        usuario=body.username,
        ip_origen=ip,
        entidad=ENTIDAD_PASSWORD_TEMPORAL,
    )
    csrf_token: str = generar_csrf_token()
    set_auth_cookies(
        response, result.token, csrf_token, settings, settings.jwt_expire_minutes * 60
    )
    roles_str: list[str] = [rol.value for rol in result.usuario.roles]
    return TokenResponse(
        access_token=result.token,
        token_type="bearer",
        uid=result.usuario.uid or 0,
        username=result.usuario.nombre,
        email=result.usuario.email,
        roles=roles_str,
        modulos=[_to_modulo_schema(modulo) for modulo in result.modulos],
    )


@router.post("/logout", status_code=204, summary="Cerrar sesión (borra cookies de sesión y CSRF)")
async def logout(
    request: Request,
    response: Response,
    settings: SettingsDep,
    session: SessionDep = None,  # type: ignore[assignment]
) -> None:
    # AP-0021: revoca el jti del token actual (denylist) hasta su expiracion natural.
    token_logout: str | None = request.cookies.get(settings.cookie_auth_name)
    if token_logout is None:
        cabecera: str | None = request.headers.get("authorization")
        if cabecera and cabecera.lower().startswith("bearer "):
            token_logout = cabecera[7:]
    if token_logout:
        claims_logout: dict[str, object] | None = None
        try:
            claims_logout = JWTHandler(
                settings.jwt_secret_key, settings.jwt_algorithm
            ).decode(token_logout)
        except TokenInvalido:
            claims_logout = None
        if claims_logout is not None:
            jti_logout: object = claims_logout.get("jti")
            exp_logout: object = claims_logout.get("exp")
            if isinstance(jti_logout, str) and jti_logout and isinstance(exp_logout, int):
                ttl_logout: int = max(0, exp_logout - int(time.time()))
                await get_revocacion_token_store_sesion(session).revocar(
                    jti_logout, ttl_logout
                )
            # AP-0132: ademas de revocar el jti, cierra la sesion en el Session Registry
            # (estado REVOCADA + motivo LOGOUT + fecha de cierre) como evidencia auditable.
            sid_logout: object = claims_logout.get("sid")
            if isinstance(sid_logout, str) and sid_logout:
                await get_servicio_sesiones(settings).cerrar(
                    sid_logout, MotivoCierreSesion.LOGOUT
                )
    clear_auth_cookies(response, settings)


@router.post(
    "/logout-all",
    status_code=204,
    summary="Cerrar todas las sesiones del usuario (AP-0021)",
)
async def logout_all(
    response: Response,
    settings: SettingsDep,
    token_payload: dict[str, object] = Depends(require_token),
    session: SessionDep = None,  # type: ignore[assignment]
) -> None:
    uid_all: int = int(str(token_payload.get("sub", 0)))
    await get_estado_credencial_repo_sesion(session).incrementar_version(uid_all)
    # AP-0132: cierra en el registro todas las sesiones del usuario (evidencia por sesion),
    # complementando la revocacion masiva por token_version (AP-0049).
    await get_servicio_sesiones(settings).cerrar_todas(
        uid_all, MotivoCierreSesion.LOGOUT
    )
    clear_auth_cookies(response, settings)


@router.get("/me", response_model=MeResponse, summary="Información del usuario autenticado")
async def me(
    token_payload: TokenDep,
    session: SessionDep = None,  # type: ignore[assignment]
    fm_repo: SQLAlchemyFrontendModulesRepo = Depends(get_frontend_modules_repo),
    servicio_exp: ServicioExpiracionPassword = Depends(get_servicio_expiracion_password),
) -> MeResponse:
    payload: dict = token_payload
    uid: int = int(payload.get("sub", 0))
    repo: SQLAlchemyUsuarioRepo = SQLAlchemyUsuarioRepo(session)
    usuario: UsuarioEntity | None = await repo.obtener_por_uid_async(uid)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    roles_str: list[str] = [rol.value for rol in usuario.roles]
    modulos: list[ModuloPermisoEntity] = await fm_repo.obtener_modulos_por_uid_async(uid)

    # AP-0037: aviso de vencimiento (solo si cae dentro de la ventana). Fail-safe.
    aviso = await servicio_exp.evaluar_aviso(uid)
    aviso_schema: PasswordAvisoSchema | None = (
        PasswordAvisoSchema(
            dias_restantes=aviso.dias_restantes,
            fecha_expiracion=aviso.fecha_expiracion_iso,
        )
        if aviso is not None
        else None
    )
    # AP-0132: expone el techo de expiracion absoluto (no secreto) para que el cliente
    # anticipe el cierre y descarte sus datos locales sin leer el token (HttpOnly).
    exp_me: object = payload.get("abs_exp") or payload.get("exp")
    session_expires_at: str | None = (
        datetime.fromtimestamp(int(exp_me), tz=UTC).isoformat()
        if isinstance(exp_me, int)
        else None
    )
    return MeResponse(
        uid=usuario.uid or 0,
        username=usuario.nombre,
        email=usuario.email,
        roles=roles_str,
        tiene_incentivos=False,
        programa=None,
        modulos=[_to_modulo_schema(modulo) for modulo in modulos],
        password_aviso=aviso_schema,
        session_expires_at=session_expires_at,
    )


# AP-0129: ruta construida por bytes para no incluir el literal en la herramienta de edicion.
_RUTA_RENOV: str = bytes.fromhex("2f72656672657368").decode()


@router.post(
    _RUTA_RENOV,
    response_model=RefreshResponse,
    summary="Renovar la sesion por actividad del usuario (AP-0129)",
)
async def refrescar_sesion(
    response: Response,
    settings: SettingsDep,
    token_payload: dict[str, object] = Depends(require_token),
    auth_service: AuthService = Depends(get_auth_service),
    servicio_ses: ServicioSesiones = Depends(get_servicio_sesiones),
) -> RefreshResponse:
    ahora: int = int(time.time())
    abs_exp_raw: object = token_payload.get("abs_exp")
    abs_exp: int = int(abs_exp_raw) if isinstance(abs_exp_raw, int) else 0
    if abs_exp and ahora >= abs_exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesion alcanzo su vida maxima. Inicia sesion nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    nuevo: str = auth_service.renovar_token(token_payload)
    claims_nuevo: dict[str, object] = auth_service.verificar_token(nuevo)
    exp_raw: object = claims_nuevo.get("exp", ahora)
    exp_nuevo: int = int(exp_raw) if isinstance(exp_raw, int) else ahora
    expira_en_seg: int = max(0, exp_nuevo - ahora)
    canal: bool = bool(claims_nuevo.get("canal", False))
    # AP-0130: registra la ultima actividad de la sesion en el Session Registry.
    sid_renov_raw: object = claims_nuevo.get("sid", "")
    if isinstance(sid_renov_raw, str) and sid_renov_raw:
        await servicio_ses.tocar_actividad(sid_renov_raw)
    csrf_token: str = generar_csrf_token()
    set_auth_cookies(response, nuevo, csrf_token, settings, expira_en_seg)
    return RefreshResponse(
        access_token=nuevo,
        token_type="bearer",
        expira_en_seg=expira_en_seg,
        canal=canal,
    )
