import { useMemo } from 'react';
import { useAuthStore } from './authStore';
import { ROLES } from '../../../shared/config/constants';
import type { AccionModulo, ModuloPermiso } from './types';

export interface PermissionsApi {
  isAuthenticated: boolean;
  isAdmin: boolean;
  roles: string[];
  modulos: ModuloPermiso[];
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
  can: (moduleCode: string, accion?: AccionModulo) => boolean;
  canVer: (moduleCode: string) => boolean;
  canCrear: (moduleCode: string) => boolean;
  canEditar: (moduleCode: string) => boolean;
  canEliminar: (moduleCode: string) => boolean;
  canExportar: (moduleCode: string) => boolean;
  canAprobar: (moduleCode: string) => boolean;
}

/**
 * Capa de consumo RBAC. Lee el usuario resuelto por el backend (roles + modulos
 * con sus 6 flags) desde el store de auth y expone helpers memorizados. Solo es
 * gating VISUAL: el backend es la autoridad real (no asumir backend seguro = el
 * front oculta, el back rechaza). Re-deriva unicamente cuando cambia el usuario.
 */
export function usePermissions(): PermissionsApi {
  const user = useAuthStore((s) => s.user);
  const puedeAcceder = useAuthStore((s) => s.puedeAcceder);
  const hasRole = useAuthStore((s) => s.hasRole);
  const modulosVisibles = useAuthStore((s) => s.modulosVisibles);

  return useMemo<PermissionsApi>(() => {
    const roles: string[] = user?.roles ?? [];
    return {
      isAuthenticated: user !== null,
      isAdmin: roles.includes(ROLES.ADMIN),
      roles,
      modulos: modulosVisibles(),
      hasRole,
      hasAnyRole: (lista: string[]) => lista.some((rol) => hasRole(rol)),
      can: (moduleCode: string, accion: AccionModulo = 'ver') => puedeAcceder(moduleCode, accion),
      canVer: (moduleCode: string) => puedeAcceder(moduleCode, 'ver'),
      canCrear: (moduleCode: string) => puedeAcceder(moduleCode, 'crear'),
      canEditar: (moduleCode: string) => puedeAcceder(moduleCode, 'editar'),
      canEliminar: (moduleCode: string) => puedeAcceder(moduleCode, 'eliminar'),
      canExportar: (moduleCode: string) => puedeAcceder(moduleCode, 'exportar'),
      canAprobar: (moduleCode: string) => puedeAcceder(moduleCode, 'aprobar'),
    };
  }, [user, puedeAcceder, hasRole, modulosVisibles]);
}