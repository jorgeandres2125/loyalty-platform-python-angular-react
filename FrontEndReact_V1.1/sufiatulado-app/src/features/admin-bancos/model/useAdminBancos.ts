import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarAdminBancoApi,
  crearAdminBancoApi,
  eliminarAdminBancoApi,
  listarAdminBancosApi,
} from './apiAdminBancos';
import type {
  AdminBancoFormPayload,
  AdminBancoFormResponse,
  AdminBancoListQuery,
  AdminBancoListResponse,
} from './types';

const QK_LIST = 'admin-bancos-list' as const;

export function useAdminBancosList(query: AdminBancoListQuery) {
  return useQuery<AdminBancoListResponse>({
    queryKey: [QK_LIST, query],
    queryFn: () => listarAdminBancosApi(query),
    staleTime: 30_000,
  });
}

export function useCrearAdminBanco() {
  const qc = useQueryClient();
  return useMutation<AdminBancoFormResponse, Error, AdminBancoFormPayload>({
    mutationFn: (payload) => crearAdminBancoApi(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useActualizarAdminBanco() {
  const qc = useQueryClient();
  return useMutation<AdminBancoFormResponse, Error, { tid: number; payload: AdminBancoFormPayload }>({
    mutationFn: ({ tid, payload }) => actualizarAdminBancoApi(tid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useEliminarAdminBanco() {
  const qc = useQueryClient();
  return useMutation<{ ok: boolean }, Error, number>({
    mutationFn: (tid) => eliminarAdminBancoApi(tid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}
