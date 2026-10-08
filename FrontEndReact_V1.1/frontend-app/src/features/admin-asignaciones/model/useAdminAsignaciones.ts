import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  asignarRolApi,
  buscarUsuariosApi,
  listarRolesAsignablesApi,
  listarUsuariosDeRolApi,
  obtenerRolesDeUsuarioApi,
  quitarRolApi,
} from './apiAdminAsignaciones';
import type { ListarParams } from './apiAdminAsignaciones';
import type {
  RolAsignableItem,
  RolDeUsuarioItem,
  UsuariosPaginaResponse,
} from './types';

const QK_ROLES = 'admin-asignaciones-roles' as const;
const QK_USUARIOS_ROL = 'admin-asignaciones-usuarios-rol' as const;
const QK_BUSCAR = 'admin-asignaciones-buscar' as const;
const QK_ROLES_USUARIO = 'admin-asignaciones-roles-usuario' as const;

export function useRolesAsignables() {
  return useQuery<RolAsignableItem[]>({
    queryKey: [QK_ROLES],
    queryFn: listarRolesAsignablesApi,
    staleTime: 60_000,
  });
}

export function useUsuariosDeRol(rid: number | null, params: ListarParams) {
  return useQuery<UsuariosPaginaResponse>({
    queryKey: [QK_USUARIOS_ROL, rid, params],
    queryFn: () => listarUsuariosDeRolApi(rid as number, params),
    enabled: rid !== null,
    staleTime: 15_000,
  });
}

export function useBuscarUsuarios(params: ListarParams, enabled: boolean) {
  return useQuery<UsuariosPaginaResponse>({
    queryKey: [QK_BUSCAR, params],
    queryFn: () => buscarUsuariosApi(params),
    enabled,
    staleTime: 15_000,
  });
}

export function useRolesDeUsuario(uid: number | null) {
  return useQuery<RolDeUsuarioItem[]>({
    queryKey: [QK_ROLES_USUARIO, uid],
    queryFn: () => obtenerRolesDeUsuarioApi(uid as number),
    enabled: uid !== null,
    staleTime: 15_000,
  });
}

export function useAsignarRol() {
  const qc = useQueryClient();
  return useMutation<void, Error, { uid: number; rid: number }>({
    mutationFn: ({ uid, rid }) => asignarRolApi(uid, rid),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QK_USUARIOS_ROL] });
      qc.invalidateQueries({ queryKey: [QK_ROLES_USUARIO] });
      qc.invalidateQueries({ queryKey: [QK_BUSCAR] });
    },
  });
}

export function useQuitarRol() {
  const qc = useQueryClient();
  return useMutation<void, Error, { uid: number; rid: number }>({
    mutationFn: ({ uid, rid }) => quitarRolApi(uid, rid),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QK_USUARIOS_ROL] });
      qc.invalidateQueries({ queryKey: [QK_ROLES_USUARIO] });
      qc.invalidateQueries({ queryKey: [QK_BUSCAR] });
    },
  });
}