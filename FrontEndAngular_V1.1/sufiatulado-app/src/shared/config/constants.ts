import { environment } from '../../environments/environment';

export const API_BASE_URL: string = environment.apiBaseUrl ?? '/api/v1';

export const APP_NAME = 'SUFI Contigo' as const;

// AP-0018: límite de 1 minuto para los formularios de autenticación. Vencido el
// plazo, se borran los datos que no se hayan enviado (login, cambio de contraseña,
// verificación de correo).
export const AUTH_FORM_TIMEOUT_MS = 60_000 as const;

// AP-0044: longitud mínima de contraseña para usuarios finales (humanos). Debe
// coincidir con PASSWORD_MIN_LONGITUD_USUARIO_FINAL del backend. Se valida al
// establecer/cambiar la clave, nunca al iniciar sesión (claves legacy más cortas
// deben seguir autenticando).
export const PASSWORD_MIN_LENGTH = 12 as const;

// AP-0051: complejidad mínima — la contraseña debe contener al menos 3 de los 4
// tipos de carácter (minúscula, mayúscula, dígito, especial). Debe coincidir con
// PASSWORD_MIN_TIPOS_CARACTER del backend.
export const PASSWORD_MIN_CHAR_TYPES = 3 as const;

// AP-0051: cuenta cuántos de los 4 tipos de carácter aparecen en la contraseña.
export function contarTiposCaracter(password: string): number {
  const tieneMinuscula = /[a-z]/.test(password);
  const tieneMayuscula = /[A-Z]/.test(password);
  const tieneDigito = /\d/.test(password);
  const tieneEspecial = /[^a-zA-Z0-9]/.test(password);
  return [tieneMinuscula, tieneMayuscula, tieneDigito, tieneEspecial].filter(Boolean).length;
}

// Clave legacy (ya NO se usa para almacenar el token: la sesión vive en cookie
// HttpOnly). Se conserva como contrato histórico y para limpieza de migración.
export const TOKEN_KEY = 'sufi_access_token' as const;
export const REFRESH_KEY = 'sufi_refresh_token' as const;

// Cookie CSRF (legible por JS, double-submit) y cabecera donde se reenvía.
// Deben coincidir con CSRF_COOKIE_NAME / CSRF_HEADER_NAME del backend.
export const CSRF_COOKIE = 'sufi_csrf' as const;
export const CSRF_HEADER = 'X-CSRF-Token' as const;

// Los roles del JWT son los `RolUsuario.value` del backend (slug con underscore),
// no los nombres legacy con espacios que están en dbo.role.name.
export const ROLES = {
  ADMIN: 'administrator',
  WEBMASTER: 'webmaster',
  COMISIONISTA: 'comisionista',
  COMISIONISTA_CONSUMO: 'comisionista_consumo',
  EJECUTIVO: 'ejecutivo_consumo',
  ASESOR_CONSUMO: 'asesor_consumo',
  ASESOR_LOGISTICO: 'asesor_logistico',
  ASESOR_COMERCIAL: 'asesor_comercial',
  ASESOR_CALLCENTER: 'asesor_callcenter',
  DOCUMENTADOR: 'documentador',
} as const;

export const TIPO_DOCUMENTO = {
  CEDULA: 4,
  RUT: 5,
  CONTRATO: 6,
} as const;

export const PROGRAMA = {
  MOVILIDAD: 1,
  CONSUMO: 2,
} as const;

export const QUERY_KEYS = {
  COMISIONISTAS: 'comisionistas',
  PERFIL_CONTACTO: 'perfil-contacto',
  PERFIL_TRIBUTARIO: 'perfil-tributario',
  PERFIL_EMOCIONAL: 'perfil-emocional',
  SAPIN_TOKEN: 'sapin-token',
  REFERENCIAS_CANALES: 'referencias-canales',
  REFERENCIAS_OFICINAS: 'referencias-oficinas',
  REFERENCIAS_EJECUTIVOS: 'referencias-ejecutivos',
  REFERENCIAS_DEPARTAMENTOS: 'referencias-departamentos',
  REFERENCIAS_CIUDADES: 'referencias-ciudades',
  DOCUMENTOS: 'documentos',
  REPORTES: 'reportes',
  ME: 'me',
  SESIONES_ACTIVAS: 'sesiones-activas',
} as const;
// AP-0206: burst limiting del lado del cliente, configurable por src/environments.
// Complementa el rate limiting del backend (slowapi, AP-0166) para evitar consumo masivo desde
// la SPA. La capacidad es la rafaga maxima; el cubo se repone a REFILL_PER_SEC por segundo.
export const RATE_LIMIT_ENABLED: boolean = environment.rateLimitEnabled !== false;
export const RATE_LIMIT_BURST: number = Number(environment.rateLimitBurst ?? 60);
export const RATE_LIMIT_REFILL_PER_SEC: number = Number(environment.rateLimitRefillPerSec ?? 10);
