import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarAdminArlApi,
  crearAdminArlApi,
  eliminarAdminArlApi,
  listarAdminArlApi,
} from './apiAdminArl';
import type {
  AdminArlFormPayload,
  AdminArlFormResponse,
  AdminArlListQuery,
  AdminArlListResponse,
} from './types';

const QK_LIST = 'admin-arl-list' as const;

export function useAdminArlList(query: AdminArlListQuery) {
  return useQuery<AdminArlListResponse>({
    queryKey: [QK_LIST, query],
    queryFn: () => listarAdminArlApi(query),
    staleTime: 30_000,
  });
}

export function useCrearAdminArl() {
  const qc = useQueryClient();
  return useMutation<AdminArlFormResponse, Error, AdminArlFormPayload>({
    mutationFn: (payload) => crearAdminArlApi(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QK_LIST] });
    },
  });
}

export function useActualizarAdminArl() {
  const qc = useQueryClient();
  return useMutation<AdminArlFormResponse, Error, { tid: number; payload: AdminArlFormPayload }>({
    mutationFn: ({ tid, payload }) => actualizarAdminArlApi(tid, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QK_LIST] });
    },
  });
}

export function useEliminarAdminArl() {
  const qc = useQueryClient();
  return useMutation<{ ok: boolean }, Error, number>({
    mutationFn: (tid) => eliminarAdminArlApi(tid),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QK_LIST] });
    },
  });
}
