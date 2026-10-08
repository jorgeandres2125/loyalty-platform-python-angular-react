import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminAutorizacionesApi } from './apiAdminAutorizaciones';
import type { AutorizacionFlagsPayload, AutorizacionModuloItem, RolItem } from './types';

const QK_ROLES = 'admin-autorizaciones-roles' as const;
const QK_MATRIZ = 'admin-autorizaciones-matriz' as const;

export function injectRolesList() {
  const api = inject(AdminAutorizacionesApi);
  return injectQuery<RolItem[]>(() => ({
    queryKey: [QK_ROLES],
    queryFn: () => api.listarRoles(),
    staleTime: 60_000,
  }));
}

export function injectMatrizPorRol(rid: () => number | null) {
  const api = inject(AdminAutorizacionesApi);
  return injectQuery<AutorizacionModuloItem[]>(() => {
    const r = rid();
    return {
      queryKey: [QK_MATRIZ, r],
      queryFn: () => api.obtenerMatriz(r as number),
      enabled: r !== null,
      staleTime: 30_000,
    };
  });
}

export function injectActualizarPermisos() {
  const api = inject(AdminAutorizacionesApi);
  const qc = inject(QueryClient);
  return injectMutation<
    AutorizacionModuloItem,
    Error,
    { rid: number; moduleId: number; payload: AutorizacionFlagsPayload }
  >(() => ({
    mutationFn: ({ rid, moduleId, payload }) => api.actualizarPermisos(rid, moduleId, payload),
    onSuccess: (_data, variables) => qc.invalidateQueries({ queryKey: [QK_MATRIZ, variables.rid] }),
  }));
}

export function injectActualizarModuloActivo() {
  const api = inject(AdminAutorizacionesApi);
  const qc = inject(QueryClient);
  return injectMutation<void, Error, { moduleId: number; activo: boolean }>(() => ({
    mutationFn: ({ moduleId, activo }) => api.actualizarModuloActivo(moduleId, activo),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_MATRIZ] }),
  }));
}
