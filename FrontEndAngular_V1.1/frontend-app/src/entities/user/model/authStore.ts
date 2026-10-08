import { Injectable, computed, signal } from '@angular/core';
import { ROLES } from '../../../shared/config/constants';
import type { AccionModulo, AuthUser, ModuloPermiso } from './types';

// Medida A (plan de remediación): el JWT vive SOLO en una cookie HttpOnly emitida
// por el backend; el cliente nunca lo almacena ni lo lee (mitiga XSS, AP-0093/0099).
// La sesión se considera activa por la presencia de `user`; el backend es la fuente
// de verdad y un 401 fuerza el regreso a /login (ver shared/api/interceptors.ts).

/** Clave de localStorage (misma que usaba el `persist` de Zustand). */
export const AUTH_STORAGE_KEY = 'sufi-auth' as const;

const FLAG_POR_ACCION: Record<AccionModulo, keyof ModuloPermiso> = {
  ver: 'puede_ver',
  crear: 'puede_crear',
  editar: 'puede_editar',
  eliminar: 'puede_eliminar',
  exportar: 'puede_exportar',
  aprobar: 'puede_aprobar',
};

// Formato compatible con zustand/persist: { state: { user }, version: 0 }.
interface EstadoPersistido {
  state?: { user?: AuthUser | null };
  version?: number;
}

function leerUsuarioPersistido(): AuthUser | null {
  try {
    const raw: string | null = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as EstadoPersistido;
    return parsed.state?.user ?? null;
  } catch {
    return null;
  }
}

function persistirUsuario(user: AuthUser | null): void {
  try {
    if (user === null) {
      window.localStorage.removeItem(AUTH_STORAGE_KEY);
      return;
    }
    const payload: EstadoPersistido = { state: { user }, version: 0 };
    window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(payload));
  } catch {
    // Modo privado o almacenamiento no disponible: el estado vive solo en memoria.
  }
}

/**
 * Store de autenticación basado en signals (equivalente al store Zustand `useAuthStore`).
 * Solo se persiste `user` (nombre/roles/módulos), que NO es el secreto de sesión.
 */
@Injectable({ providedIn: 'root' })
export class AuthStore {
  private readonly _user = signal<AuthUser | null>(leerUsuarioPersistido());
  private readonly _sapinToken = signal<string | null>(null);

  readonly user = this._user.asReadonly();
  readonly sapinToken = this._sapinToken.asReadonly();

  readonly isAuthenticated = computed<boolean>(() => this._user() !== null);
  readonly roles = computed<string[]>(() => this._user()?.roles ?? []);
  readonly isAdmin = computed<boolean>(() => this.roles().includes(ROLES.ADMIN));

  readonly modulosVisibles = computed<ModuloPermiso[]>(() => {
    const user = this._user();
    if (!user) return [];
    return [...user.modulos].filter((modulo) => modulo.puede_ver).sort((a, b) => a.orden - b.orden);
  });

  readonly canAccessSapin = computed<boolean>(() => {
    const user = this._user();
    if (!user) return false;
    const sapinRoles: string[] = [ROLES.COMISIONISTA, ROLES.COMISIONISTA_CONSUMO];
    return sapinRoles.some((role) => user.roles.includes(role)) && user.tiene_incentivos;
  });

  setAuth(user: AuthUser): void {
    this._user.set(user);
    persistirUsuario(user);
  }

  setSapinToken(token: string): void {
    this._sapinToken.set(token);
  }

  logout(): void {
    // El borrado de la cookie de sesión lo hace el backend (POST /auth/logout).
    // Se elimina por completo la clave 'sufi-auth' de localStorage.
    this._user.set(null);
    this._sapinToken.set(null);
    persistirUsuario(null);
  }

  hasRole(role: string): boolean {
    return this._user()?.roles.includes(role) ?? false;
  }

  puedeAcceder(moduleCode: string, accion: AccionModulo = 'ver'): boolean {
    const user = this._user();
    if (!user) return false;
    if (user.roles.includes(ROLES.ADMIN)) return true;
    const modulo = user.modulos?.find((mod) => mod.module_code === moduleCode);
    if (!modulo) return false;
    return Boolean(modulo[FLAG_POR_ACCION[accion]]);
  }
}
