import type { AuthUser, ModuloPermiso } from '../entities/user/model/types';

/**
 * Construye un `ModuloPermiso` con todos los flags en `false` por defecto;
 * pasa `overrides` para encender solo lo que la prueba necesita.
 */
export function makeModulo(overrides: Partial<ModuloPermiso> = {}): ModuloPermiso {
  return {
    module_id: 1,
    module_code: 'DASHBOARD',
    nombre: 'Dashboard',
    ruta: '/dashboard',
    icono: 'bi-speedometer2',
    orden: 1,
    puede_ver: true,
    puede_crear: false,
    puede_editar: false,
    puede_eliminar: false,
    puede_exportar: false,
    puede_aprobar: false,
    ...overrides,
  };
}

/**
 * Construye un `AuthUser` válido (pasa los type guards) con un módulo por
 * defecto; pasa `overrides` para ajustar roles, incentivos, módulos, etc.
 */
export function makeAuthUser(overrides: Partial<AuthUser> = {}): AuthUser {
  return {
    uid: 100,
    username: 'jdoe',
    email: 'jdoe@sufi.test',
    roles: ['comisionista'],
    tiene_incentivos: false,
    programa: 1,
    modulos: [makeModulo()],
    ...overrides,
  };
}

/**
 * Genera un JWT de juguete (header.payload.signature) cuyo claim `exp`
 * vence dentro de `secondsFromNow` segundos. Solo el segmento payload es
 * relevante para `isTokenValido` del authStore.
 */
export function makeJwt(secondsFromNow: number): string {
  const exp: number = Math.floor(Date.now() / 1000) + secondsFromNow;
  const payload: string = btoa(JSON.stringify({ exp }));
  return `header.${payload}.signature`;
}
