import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarAdminAfpApi,
  crearAdminAfpApi,
  eliminarAdminAfpApi,
  listarAdminAfpApi,
} from './apiAdminAfp';
import type {
  AdminAfpFormPayload,
  AdminAfpFormResponse,
  AdminAfpListQuery,
  AdminAfpListResponse,
} from './types';

const QK_LIST = 'admin-afp-list' as const;

export function useAdminAfpList(query: AdminAfpListQuery) {
  return useQuery<AdminAfpListResponse>({
    queryKey: [QK_LIST, query],
    queryFn: () => listarAdminAfpApi(query),
    staleTime: 30_000,
  });
}

export function useCrearAdminAfp() {
  const qc = useQueryClient();
  return useMutation<AdminAfpFormResponse, Error, AdminAfpFormPayload>({
    mutationFn: (payload) => crearAdminAfpApi(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QK_LIST] });
    },
  });
}

export function useActualizarAdminAfp() {
  const qc = useQueryClient();
  return useMutation<
    AdminAfpFormResponse,
    Error,
    { tid: number; payload: AdminAfpFormPayload }
  >({
    mutationFn: ({ tid, payload }) => actualizarAdminAfpApi(tid, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QK_LIST] });
    },
  });
}

export function useEliminarAdminAfp() {
  const qc = useQueryClient();
  return useMutation<{ ok: boolean }, Error, number>({
    mutationFn: (tid) => eliminarAdminAfpApi(tid),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QK_LIST] });
    },
  });
}
