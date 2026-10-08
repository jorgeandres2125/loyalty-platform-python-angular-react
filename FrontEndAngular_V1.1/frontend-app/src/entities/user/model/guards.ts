import type { AuthUser, ModuloPermiso, PasswordAviso, TokenResponse } from './types';

function isModuloPermiso(value: unknown): value is ModuloPermiso {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    typeof obj.module_id === 'number' &&
    typeof obj.module_code === 'string' &&
    typeof obj.nombre === 'string' &&
    typeof obj.orden === 'number' &&
    typeof obj.puede_ver === 'boolean'
  );
}

function isPasswordAviso(value: unknown): value is PasswordAviso {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    typeof obj.dias_restantes === 'number' &&
    typeof obj.fecha_expiracion === 'string'
  );
}

export function isAuthUser(value: unknown): value is AuthUser {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  // AP-0037: password_aviso es opcional; si viene, debe ser null o un aviso valido.
  const avisoOk =
    obj.password_aviso === undefined ||
    obj.password_aviso === null ||
    isPasswordAviso(obj.password_aviso);
  return (
    typeof obj.uid === 'number' &&
    typeof obj.username === 'string' &&
    typeof obj.email === 'string' &&
    Array.isArray(obj.roles) &&
    obj.roles.every((role) => typeof role === 'string') &&
    typeof obj.tiene_incentivos === 'boolean' &&
    (obj.programa === null || typeof obj.programa === 'number') &&
    Array.isArray(obj.modulos) &&
    obj.modulos.every(isModuloPermiso) &&
    avisoOk
  );
}

export function isTokenResponse(value: unknown): value is TokenResponse {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    typeof obj.access_token === 'string' &&
    obj.access_token.length > 0 &&
    typeof obj.token_type === 'string' &&
    typeof obj.uid === 'number' &&
    typeof obj.username === 'string' &&
    typeof obj.email === 'string' &&
    Array.isArray(obj.roles) &&
    Array.isArray(obj.modulos)
  );
}
