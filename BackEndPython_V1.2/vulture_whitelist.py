# -*- coding: utf-8 -*-
# AP-0110 -- Whitelist de vulture: simbolos reportados como 'no usados' que SI son
# codigo vivo o andamiaje intencional. NO es codigo ejecutable; solo lo lee vulture
# (ver [tool.vulture] en pyproject.toml). Excluido de ruff/mypy (extend-exclude).
#
# Categorias y justificacion:
#  - Campos de schemas Pydantic (response/request): los lee FastAPI al serializar.
#  - Columnas y relaciones SQLAlchemy (mapped_column/relationship): las usa el ORM.
#  - Escrituras de atributos de openpyxl/pypdf/LogRecord: efectos colaterales de
#    libreria (limpieza de metadatos AP-0085, redaccion de logs AP-0087).
#  - Miembros de enum del contrato de dominio (TipoDocumento 4=Cedula/5=RUT/6=Contrato...).
#  - Andamiaje por tabla (1 Entity/Model/Port/Repository por tabla del catalogo):
#    ComisionistaPrograma/Subprograma, AesPasswordEntity, metodos de puerto extra.
#  - Paridad cripto SAPIN (AES-256-CBC de password): requisito de migracion documentado.
#  - Capacidades con DI lista y pendientes de endpoint (get_enviar_correo_masivo_uc, AP-0088;
#    verificar_token con pruebas; validar_acceso_programa; propiedades de Settings).
#
# Regenerar: python -m vulture src --make-whitelist > vulture_whitelist.py
#            (luego volver a anteponer esta cabecera).

canal  # unused variable (src\adapters\api\schemas\asesor_consumo\asesor_consumo_item.py:25)
oficina  # unused variable (src\adapters\api\schemas\asesor_consumo\asesor_consumo_item.py:26)
movilidad  # unused variable (src\adapters\api\schemas\dashboard\dashboard_stats_response.py:10)
consumo  # unused variable (src\adapters\api\schemas\dashboard\dashboard_stats_response.py:11)
activos  # unused variable (src\adapters\api\schemas\dashboard\programa_stats_schema.py:9)
incompletos  # unused variable (src\adapters\api\schemas\dashboard\programa_stats_schema.py:10)
con_incentivos  # unused variable (src\adapters\api\schemas\dashboard\programa_stats_schema.py:11)
nuevos_mes  # unused variable (src\adapters\api\schemas\dashboard\programa_stats_schema.py:12)
user  # unused variable (src\adapters\api\schemas\debug\database_settings_view.py:12)
password_length  # unused variable (src\adapters\api\schemas\debug\database_settings_view.py:14)
pool_min  # unused variable (src\adapters\api\schemas\debug\database_settings_view.py:15)
pool_max  # unused variable (src\adapters\api\schemas\debug\database_settings_view.py:16)
expire_minutes  # unused variable (src\adapters\api\schemas\debug\jwt_settings_view.py:10)
secret_key_length  # unused variable (src\adapters\api\schemas\debug\jwt_settings_view.py:11)
secret_key_is_default  # unused variable (src\adapters\api\schemas\debug\jwt_settings_view.py:12)
aes_key_ctr_configured  # unused variable (src\adapters\api\schemas\debug\sapin_settings_view.py:10)
aes_iv_ctr_configured  # unused variable (src\adapters\api\schemas\debug\sapin_settings_view.py:11)
aes_key_cbc_configured  # unused variable (src\adapters\api\schemas\debug\sapin_settings_view.py:12)
env_files  # unused variable (src\adapters\api\schemas\debug\settings_debug_response.py:15)
env_files_existen  # unused variable (src\adapters\api\schemas\debug\settings_debug_response.py:16)
database  # unused variable (src\adapters\api\schemas\debug\settings_debug_response.py:21)
sapin  # unused variable (src\adapters\api\schemas\debug\settings_debug_response.py:22)
tipo_nombre  # unused variable (src\adapters\api\schemas\documento\documento_edit_response.py:14)
tiene_incentivos  # unused variable (src\adapters\api\schemas\me_response_schema.py:15)
access_token  # unused variable (src\adapters\api\schemas\token_response_schema.py:11)
token_type  # unused variable (src\adapters\api\schemas\token_response_schema.py:12)
verificado  # unused variable (src\adapters\api\schemas\verificacion_email\confirmar_codigo_response.py:9)
base_datos  # AP-0081 -- campo de EstadoDisponibilidadResponse (FastAPI lo serializa en /health/ready)
verificado  # unused variable (src\application\dto\resultado_verificacion_dto.py:10)
hc_uid  # unused variable (src\domain\entities\historico_correo_entity.py:20)
password_hash  # unused variable (src\domain\entities\usuario_entity.py:15)
_.listar_todos_async  # unused method (src\domain\ports\outbound\afp_repository.py:23)
_.listar_pendientes_async  # unused method (src\domain\ports\outbound\documento_repository.py:21)
_.obtener_ejecutivo_async  # unused method (src\domain\ports\outbound\referencia_repository.py:17)
actualizado_en_monotonic  # unused variable (src\domain\value_objects\intentos_login.py:16)
CEDULA  # unused variable (src\domain\value_objects\tipo_documento.py:5)
RUT  # unused variable (src\domain\value_objects\tipo_documento.py:6)
CONTRATO  # unused variable (src\domain\value_objects\tipo_documento.py:7)
EPS  # unused variable (src\domain\value_objects\tipo_documento.py:8)
AFP  # unused variable (src\domain\value_objects\tipo_documento.py:9)
ARL  # unused variable (src\domain\value_objects\tipo_documento.py:10)
PREPAGADA  # unused variable (src\domain\value_objects\tipo_documento.py:11)
VIVIENDA  # unused variable (src\domain\value_objects\tipo_documento.py:12)
PENSIONVOL  # unused variable (src\domain\value_objects\tipo_documento.py:13)
AFC  # unused variable (src\domain\value_objects\tipo_documento.py:14)
DEPENDIENTES  # unused variable (src\domain\value_objects\tipo_documento.py:15)
generado_en  # unused variable (src\domain\value_objects\token_sapin.py:9)
ssl_certfile  # unused variable (src\infrastructure\config\settings.py:187)
ssl_keyfile  # unused variable (src\infrastructure\config\settings.py:188)
_.metadata  # unused attribute (src\infrastructure\files\sanitizador_metadatos_archivo.py:39)
_.xmp_metadata  # unused attribute (src\infrastructure\files\sanitizador_metadatos_archivo.py:40)
_.creator  # unused attribute (src\infrastructure\files\sanitizador_metadatos_archivo.py:52)
_.lastModifiedBy  # unused attribute (src\infrastructure\files\sanitizador_metadatos_archivo.py:53)
_.title  # unused attribute (src\infrastructure\files\sanitizador_metadatos_archivo.py:54)
_.subject  # unused attribute (src\infrastructure\files\sanitizador_metadatos_archivo.py:55)
_.description  # unused attribute (src\infrastructure\files\sanitizador_metadatos_archivo.py:56)
_.keywords  # unused attribute (src\infrastructure\files\sanitizador_metadatos_archivo.py:57)
_.category  # unused attribute (src\infrastructure\files\sanitizador_metadatos_archivo.py:58)
_.properties  # unused attribute (src\infrastructure\files\sanitizador_metadatos_archivo.py:59)
_.msg  # unused attribute (src\infrastructure\logging\redaccion_sensible_filter.py:46)
_.args  # unused attribute (src\infrastructure\logging\redaccion_sensible_filter.py:47)
cod_canales_oficinas  # unused variable (src\infrastructure\persistence\models\canal_oficina_model.py:19)
canal  # unused variable (src\infrastructure\persistence\models\canal_oficina_model.py:27)
oficina  # unused variable (src\infrastructure\persistence\models\canal_oficina_model.py:28)
created  # unused variable (src\infrastructure\persistence\models\drupal_user_model.py:19)
descripcion  # unused variable (src\infrastructure\persistence\models\frontend_module_model.py:22)
created  # unused variable (src\infrastructure\persistence\models\frontend_module_model.py:27)
changed  # unused variable (src\infrastructure\persistence\models\frontend_module_model.py:30)
created  # unused variable (src\infrastructure\persistence\models\frontend_module_permission_model.py:41)
changed  # unused variable (src\infrastructure\persistence\models\frontend_module_permission_model.py:44)
hc_uid  # unused variable (src\infrastructure\persistence\models\historico_correo_model.py:17)
banco_ref  # unused variable (src\infrastructure\persistence\models\perfil_contacto_model.py:98)
canal  # unused variable (src\infrastructure\persistence\models\perfil_contacto_model.py:99)
oficina  # unused variable (src\infrastructure\persistence\models\perfil_contacto_model.py:100)
fallback  # unused variable (src\infrastructure\persistence\repositories\sqlalchemy_autorizaciones_repo.py:85)
_.creator  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:113)
_.lastModifiedBy  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:114)
_.title  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:115)
_.subject  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:116)
_.description  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:117)
_.keywords  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:118)
_.category  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:119)
_.properties  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:120)
_.title  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:131)
_.font  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:134)
_.fill  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:135)
_.alignment  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:136)
_.width  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:137)
_.number_format  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:142)
_.freeze_panes  # unused attribute (src\infrastructure\reporting\excel_report_generator.py:143)
SUFIJO_CIFRADO  # unused variable (src\shared\constants\cifrado.py:12)
CAMPOS_RESTRINGIDOS  # unused variable (src\shared\constants\cifrado.py:14)
ESTADOS_DOCUMENTO_VALIDOS  # unused variable (src\shared\constants\tipos_documento.py:33)
_.verificar_token  # unused method (src\application\services\auth_service.py:38)
get_usuario_repo  # unused function (src\infrastructure\config\dependencies.py:213)
get_enviar_correo_masivo_uc  # unused function (src\infrastructure\config\dependencies.py:475)
get_almacen_efimero  # AP-0081 -- factory del almacen efimero compartido (Redis o memoria) para HA multi-replica; mecanismo listo, cableado por-store (OTP/OOB/throttle) es incremental
_.is_production  # unused property (src\infrastructure\config\settings.py:226)
_.is_development  # unused property (src\infrastructure\config\settings.py:230)
_.listar_todos_async  # unused method (src\infrastructure\persistence\repositories\sqlalchemy_afp_repo.py:50)
AesPasswordEntity  # unused class (src\domain\entities\aes_password_entity.py:6)
_.listar_pendientes_async  # unused method (src\infrastructure\persistence\repositories\sqlalchemy_documento_repo.py:153)
ComisionistaProgramaRepository  # unused class (src\domain\ports\outbound\comisionista_programa_repository.py:8)
ComisionistaSubprogramaRepository  # unused class (src\domain\ports\outbound\comisionista_subprograma_repository.py:8)
_genero_letter  # unused function (src\infrastructure\reporting\excel_report_generator.py:156)
validar_acceso_programa  # unused function (src\domain\services\validador_programas.py:20)
_.descifrar_password_cbc  # unused method (src\domain\services\crypto_sapin.py:27)
_.cifrar_password_cbc  # unused method (src\domain\services\crypto_sapin.py:37)
Cedula  # unused class (src\domain\value_objects\cedula.py:5)
NIT  # unused class (src\domain\value_objects\nit.py:5)
_.obtener_ejecutivo_async  # unused method (src\infrastructure\persistence\repositories\sqlalchemy_referencia_repo.py:48)
get_current_user  # unused function (src\adapters\api\middleware\auth_middleware.py:10)
TipoDocumento  # unused class (src\domain\value_objects\tipo_documento.py:4)
SQLAlchemyComisionistaProgramaRepo  # unused class (src\infrastructure\persistence\repositories\sqlalchemy_comisionista_programa_repo.py:10)
SQLAlchemyComisionistaSubprogramaRepo  # unused class (src\infrastructure\persistence\repositories\sqlalchemy_comisionista_subprograma_repo.py:10)
max_upload_mb  # AP-0137: campo de schema Pydantic (FastAPI lo serializa en la respuesta)
verificacion_habilitada  # AP-0144: campo de schema Pydantic (FastAPI lo serializa)
CifradoCbcConRelleno  # AP-0178 -- cifrado CBC con relleno aleatorio para datos pequenos (listo, pendiente de cableado en endpoint)
_.en_blacklist  # AP-0159 -- metodo publico de consulta de blacklist (usado en pruebas; vulture no escanea tests)
_.cifrar_clave_datos  # AP-0180 -- contraparte (envolver DEK) del puerto KMS; la usa el tooling de operacion para generar app_encryption_key_wrapped
_.respaldado_por_hsm  # AP-0180 -- atributo de contrato del puerto GestorClaveMaestra para diagnostico/auditoria
_.principal_certificado  # AP-0003 -- atributo puesto en request.state por el middleware mTLS; lo consume el handler downstream (probado en tests; vulture no escanea tests)
SMS  # AP-0005 -- canal OOB declarado para fase 2 (multicanal); miembro de enum
PUSH  # AP-0005 -- canal OOB declarado para fase 3 (app movil); miembro de enum
EXPIRADA  # AP-0005 -- estado del ciclo de vida OOB (el store lo representa con None); miembro de enum
EJECUTADA  # AP-0005 -- estado que fija el motor de transacciones tras liberar; miembro de enum
CAMBIO_CUENTA_BANCARIA  # AP-0005 -- tipo de transaccion critica (catalogo); usado via valor y Pydantic
CAMBIO_CORREO  # AP-0005 -- tipo de transaccion critica (catalogo)
ALTA_USUARIO_PRIVILEGIADO  # AP-0005 -- tipo de transaccion critica (catalogo)
CAMBIO_PERMISOS  # AP-0005 -- tipo de transaccion critica (catalogo)
INACTIVACION_USUARIO  # AP-0005 -- tipo de transaccion critica (catalogo)
creado_en_iso  # AP-0006 -- campo de EvidenciaFirma (timestamp en la cadena de evidencias; leido en pruebas y por consumidores)
ES384  # AP-0006 -- algoritmo de firma declarado para casos de mayor valor; miembro de enum
EDDSA  # AP-0006 -- algoritmo Ed25519 declarado para interoperabilidad; miembro de enum
lockout_notify_user_on_lock  # AP-0009 -- config de notificacion al usuario (cableado de notificaciones, fase siguiente)
lockout_notify_admin_on_lock  # AP-0009 -- config de notificacion al admin (cableado de notificaciones, fase siguiente)
SQLAlchemyBloqueoCuentaRepo  # AP-0009 -- adaptador SQL durable (tabla user_lockout) listo, pendiente de cableado; el wired por defecto es InMemoryBloqueoCuentaRepo
updated_at  # AP-0021 -- columna de auditoria de user_token_version (write-only; la consultan DBAs)
_.updated_at  # AP-0021 -- escritura de la columna de auditoria updated_at en el repo SQL
CLAIM_AUTH_EPOCH  # AP-0021 -- claim auth_epoch declarado (politica de inactividad, fase siguiente)
SQLAlchemyEstadoCredencialRepo  # AP-0021 -- adaptador SQL durable (user_token_version) listo, pendiente de cableado
SQLAlchemyRevocacionTokenRepo  # AP-0021 -- adaptador SQL durable (revoked_token) listo, pendiente de cableado
first_login  # AP-0014 -- campo de DispositivoResponse (FastAPI lo serializa)
last_login  # AP-0014 -- campo de DispositivoResponse (FastAPI lo serializa)
es_nuevo  # AP-0014 -- campo de ResultadoDispositivoDTO (indica equipo nuevo; leido en pruebas)
SQLAlchemyDispositivoRepo  # AP-0014 -- adaptador SQL durable (SECURITY_USER_DEVICE) listo, pendiente de cableado
dividir_kek  # unused method (AP-0015 ceremonia de alta de shares, ejercitada en tests)
InMemoryAuditoriaRepo  # unused class (AP-0028 adaptador en memoria para pruebas; SQL cableado en produccion)

# AP-0037: aviso de vencimiento de contrasena
password_aviso  # unused variable (campo Pydantic de MeResponse leido por FastAPI)
InMemoryPasswordExpiracionRepo  # unused class (adaptador en memoria para pruebas; SQL cableado en produccion)

# AP-0041: historial de contrasenas
InMemoryPasswordHistoryRepo  # unused class (adaptador en memoria para pruebas; SQL cableado en produccion)

# AP-0046, AP-0047 y AP-0048: contrasenas temporales
InMemoryPasswordTemporalRepo  # unused class (adaptador en memoria para pruebas; SQL cableado en produccion)
ADMIN  # AP-0047 -- origen de la temporal; miembro de enum construido por valor desde la API
SOPORTE  # AP-0047 -- origen de la temporal; miembro de enum construido por valor desde la API
SISTEMA  # AP-0047 -- origen reservado a la provision automatica de usuarios; miembro de enum

# AP-0062: custodia y rotacion de credenciales privilegiadas via PAM
reiniciar_engine_por_rotacion  # AP-0062 -- reinicio del pool para tolerar rotacion de credencial por el broker PAM (listo, pendiente de cableado al disparador de recuperacion ante fallo de auth cuando se integre PAM)

# AP-0075: versionamiento del token SAPIN hacia AES-256
_.descifrar_v2  # AP-0075 -- validacion e interoperabilidad del token v2 (AES-256-GCM), ejercitada en pruebas; vulture no escanea tests
_._crypto  # AP-0075 -- auth_service conserva la referencia a CryptoSAPIN para la migracion de passwords legacy AES-256-CBC (descifrar_password_cbc, ya listado); quedo visible al renombrar el atributo del emisor de token; pendiente de cableado

# AP-0130: sesiones concurrentes (Session Registry)
es_actual  # AP-0130 -- campo de SesionResponse (FastAPI lo serializa; indica si la fila es la sesion de la peticion actual)
jti_actual  # AP-0130 -- campo de SesionActiva que asocia el jti vigente a la sesion (JWT-sesion); write-only en el Quick Win, pendiente de cableado para deteccion de reuse de refresh en Fase 2

# AP-0132: descarte de datos de sesion (ciclo de vida y cierre auditable del Session Registry)
fecha_cierre  # AP-0132 -- campo de SesionActiva: momento del cierre; evidencia auditable consumida por el adaptador SQL y la auditoria, no por otro codigo src
motivo_cierre  # AP-0132 -- campo de SesionActiva: causa del cierre (logout, expiracion, etc.); evidencia auditable para persistencia y reportes
_.motivo_cierre  # AP-0132 -- escritura del motivo de cierre en el Session Registry (InMemory) al cerrar la sesion
_.fecha_cierre  # AP-0132 -- escritura de la fecha de cierre en el Session Registry (InMemory) al cerrar la sesion
INACTIVIDAD  # AP-0132 -- motivo de cierre por inactividad (idle, AP-0129); miembro de enum del catalogo de motivos
REVOCACION_ADMIN  # AP-0132 -- motivo de cierre por revocacion administrativa (reset admin, AP-0049); miembro de enum del catalogo
CAMBIO_CREDENCIAL  # AP-0132 -- motivo de cierre por cambio de credencial (AP-0020); miembro de enum del catalogo
# AP-0157: bloqueo suave y bloqueo duro de cuentas
SQLAlchemyBloqueoDuroRepo  # AP-0157 -- adaptador SQL durable (tabla user_account_lock) listo, pendiente de cableado; el wired por defecto es InMemoryBloqueoDuroRepo
is_soft_locked  # AP-0157 -- campo de EstadoBloqueoResponse (FastAPI lo serializa)
soft_lock_reason  # AP-0157 -- campo de EstadoBloqueoResponse (FastAPI lo serializa)
soft_lock_expiration_epoch  # AP-0157 -- campo de EstadoBloqueoResponse (FastAPI lo serializa)
is_hard_locked  # AP-0157 -- campo de EstadoBloqueoResponse (FastAPI lo serializa)
hard_lock_reason  # AP-0157 -- campo de EstadoBloqueoResponse (FastAPI lo serializa)
