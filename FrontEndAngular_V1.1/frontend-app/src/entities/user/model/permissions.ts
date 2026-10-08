import { Injectable, inject } from '@angular/core';
import { AuthStore } from './authStore';
import type { AccionModulo } from './types';

/**
 * Capa de consumo RBAC (equivalente al hook `usePermissions`). Lee el usuario resuelto
 * por el backend (roles + modulos con sus 6 flags) desde el AuthStore. Solo es gating
 * VISUAL: el backend es la autoridad real (el front oculta, el back rechaza).
 * Todos los métodos leen signals, por lo que son reactivos dentro de templates/computed.
 */
@Injectable({ providedIn: 'root' })
export class Permissions {
  private readonly auth = inject(AuthStore);

  readonly isAuthenticated = this.auth.isAuthenticated;
  readonly isAdmin = this.auth.isAdmin;
  readonly roles = this.auth.roles;
  readonly modulos = this.auth.modulosVisibles;

  hasRole(role: string): boolean {
    return this.auth.hasRole(role);
  }

  hasAnyRole(lista: string[]): boolean {
    return lista.some((rol) => this.auth.hasRole(rol));
  }

  can(moduleCode: string, accion: AccionModulo = 'ver'): boolean {
    return this.auth.puedeAcceder(moduleCode, accion);
  }

  canVer(moduleCode: string): boolean {
    return this.can(moduleCode, 'ver');
  }

  canCrear(moduleCode: string): boolean {
    return this.can(moduleCode, 'crear');
  }

  canEditar(moduleCode: string): boolean {
    return this.can(moduleCode, 'editar');
  }

  canEliminar(moduleCode: string): boolean {
    return this.can(moduleCode, 'eliminar');
  }

  canExportar(moduleCode: string): boolean {
    return this.can(moduleCode, 'exportar');
  }

  canAprobar(moduleCode: string): boolean {
    return this.can(moduleCode, 'aprobar');
  }
}
