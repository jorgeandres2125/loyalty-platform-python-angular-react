import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarAdminDepartamentoApi,
  crearAdminDepartamentoApi,
  eliminarAdminDepartamentoApi,
  listarAdminDepartamentosApi,
} from './apiAdminDepartamentos';
import type {
  AdminDepartamentoFormPayload,
  AdminDepartamentoFormResponse,
  AdminDepartamentoListQuery,
  AdminDepartamentoListResponse,
} from './types';

const QK_LIST = 'admin-departamentos-list' as const;

export function useAdminDepartamentosList(query: AdminDepartamentoListQuery) {
  return useQuery<AdminDepartamentoListResponse>({
    queryKey: [QK_LIST, query],
    queryFn: () => listarAdminDepartamentosApi(query),
    staleTime: 30_000,
  });
}

export function useCrearAdminDepartamento() {
  const qc = useQueryClient();
  return useMutation<AdminDepartamentoFormResponse, Error, AdminDepartamentoFormPayload>({
    mutationFn: (payload) => crearAdminDepartamentoApi(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useActualizarAdminDepartamento() {
  const qc = useQueryClient();
  return useMutation<AdminDepartamentoFormResponse, Error, { did: number; payload: AdminDepartamentoFormPayload }>({
    mutationFn: ({ did, payload }) => actualizarAdminDepartamentoApi(did, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useEliminarAdminDepartamento() {
  const qc = useQueryClient();
  return useMutation<{ ok: boolean }, Error, number>({
    mutationFn: (did) => eliminarAdminDepartamentoApi(did),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}
