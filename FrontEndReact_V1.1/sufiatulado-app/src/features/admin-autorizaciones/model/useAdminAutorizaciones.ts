import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarModuloActivoApi,
  actualizarPermisosApi,
  listarRolesApi,
  obtenerMatrizApi,
} from './apiAdminAutorizaciones';
import type { AutorizacionFlagsPayload, AutorizacionModuloItem, RolItem } from './types';

const QK_ROLES = 'admin-autorizaciones-roles' as const;
const QK_MATRIZ = 'admin-autorizaciones-matriz' as const;

export function useRolesList() {
  return useQuery<RolItem[]>({
    queryKey: [QK_ROLES],
    queryFn: listarRolesApi,
    staleTime: 60_000,
  });
}

export function useMatrizPorRol(rid: number | null) {
  return useQuery<AutorizacionModuloItem[]>({
    queryKey: [QK_MATRIZ, rid],
    queryFn: () => obtenerMatrizApi(rid as number),
    enabled: rid !== null,
    staleTime: 30_000,
  });
}

export function useActualizarPermisos() {
  const qc = useQueryClient();
  return useMutation<
    AutorizacionModuloItem,
    Error,
    { rid: number; moduleId: number; payload: AutorizacionFlagsPayload }
  >({
    mutationFn: ({ rid, moduleId, payload }) => actualizarPermisosApi(rid, moduleId, payload),
    onSuccess: (_data, variables) =>
      qc.invalidateQueries({ queryKey: [QK_MATRIZ, variables.rid] }),
  });
}

export function useActualizarModuloActivo() {
  const qc = useQueryClient();
  return useMutation<void, Error, { moduleId: number; activo: boolean }>({
    mutationFn: ({ moduleId, activo }) => actualizarModuloActivoApi(moduleId, activo),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_MATRIZ] }),
  });
}
