import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarAdminProfesionApi,
  crearAdminProfesionApi,
  eliminarAdminProfesionApi,
  listarAdminProfesionesApi,
} from './apiAdminProfesiones';
import type {
  AdminProfesionFormPayload,
  AdminProfesionFormResponse,
  AdminProfesionListQuery,
  AdminProfesionListResponse,
} from './types';

const QK_LIST = 'admin-profesiones-list' as const;

export function useAdminProfesionesList(query: AdminProfesionListQuery) {
  return useQuery<AdminProfesionListResponse>({
    queryKey: [QK_LIST, query],
    queryFn: () => listarAdminProfesionesApi(query),
    staleTime: 30_000,
  });
}

export function useCrearAdminProfesion() {
  const qc = useQueryClient();
  return useMutation<AdminProfesionFormResponse, Error, AdminProfesionFormPayload>({
    mutationFn: (payload) => crearAdminProfesionApi(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useActualizarAdminProfesion() {
  const qc = useQueryClient();
  return useMutation<AdminProfesionFormResponse, Error, { tid: number; payload: AdminProfesionFormPayload }>({
    mutationFn: ({ tid, payload }) => actualizarAdminProfesionApi(tid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useEliminarAdminProfesion() {
  const qc = useQueryClient();
  return useMutation<{ ok: boolean }, Error, number>({
    mutationFn: (tid) => eliminarAdminProfesionApi(tid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}
