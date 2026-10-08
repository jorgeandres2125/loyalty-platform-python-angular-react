import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarAdminSubprogramaApi,
  crearAdminSubprogramaApi,
  eliminarAdminSubprogramaApi,
  listarAdminSubprogramasApi,
} from './apiAdminSubprogramas';
import type {
  AdminSubprogramaFormPayload,
  AdminSubprogramaFormResponse,
  AdminSubprogramaListQuery,
  AdminSubprogramaListResponse,
} from './types';

const QK_LIST = 'admin-subprogramas-list' as const;

export function useAdminSubprogramasList(query: AdminSubprogramaListQuery) {
  return useQuery<AdminSubprogramaListResponse>({
    queryKey: [QK_LIST, query],
    queryFn: () => listarAdminSubprogramasApi(query),
    staleTime: 30_000,
  });
}

export function useCrearAdminSubprograma() {
  const qc = useQueryClient();
  return useMutation<AdminSubprogramaFormResponse, Error, AdminSubprogramaFormPayload>({
    mutationFn: (payload) => crearAdminSubprogramaApi(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useActualizarAdminSubprograma() {
  const qc = useQueryClient();
  return useMutation<AdminSubprogramaFormResponse, Error, { cspid: number; payload: AdminSubprogramaFormPayload }>({
    mutationFn: ({ cspid, payload }) => actualizarAdminSubprogramaApi(cspid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useEliminarAdminSubprograma() {
  const qc = useQueryClient();
  return useMutation<{ ok: boolean }, Error, number>({
    mutationFn: (cspid) => eliminarAdminSubprogramaApi(cspid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}
