import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarAdminEpsApi,
  crearAdminEpsApi,
  eliminarAdminEpsApi,
  listarAdminEpsApi,
} from './apiAdminEps';
import type {
  AdminEpsFormPayload,
  AdminEpsFormResponse,
  AdminEpsListQuery,
  AdminEpsListResponse,
} from './types';

const QK_LIST = 'admin-eps-list' as const;

export function useAdminEpsList(query: AdminEpsListQuery) {
  return useQuery<AdminEpsListResponse>({
    queryKey: [QK_LIST, query],
    queryFn: () => listarAdminEpsApi(query),
    staleTime: 30_000,
  });
}

export function useCrearAdminEps() {
  const qc = useQueryClient();
  return useMutation<AdminEpsFormResponse, Error, AdminEpsFormPayload>({
    mutationFn: (payload) => crearAdminEpsApi(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useActualizarAdminEps() {
  const qc = useQueryClient();
  return useMutation<AdminEpsFormResponse, Error, { tid: number; payload: AdminEpsFormPayload }>({
    mutationFn: ({ tid, payload }) => actualizarAdminEpsApi(tid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useEliminarAdminEps() {
  const qc = useQueryClient();
  return useMutation<{ ok: boolean }, Error, number>({
    mutationFn: (tid) => eliminarAdminEpsApi(tid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}
