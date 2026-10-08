import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarAdminCiudadApi,
  crearAdminCiudadApi,
  eliminarAdminCiudadApi,
  listarAdminCiudadesApi,
} from './apiAdminCiudades';
import type {
  AdminCiudadFormPayload,
  AdminCiudadFormResponse,
  AdminCiudadListQuery,
  AdminCiudadListResponse,
} from './types';

const QK_LIST = 'admin-ciudades-list' as const;

export function useAdminCiudadesList(query: AdminCiudadListQuery) {
  return useQuery<AdminCiudadListResponse>({
    queryKey: [QK_LIST, query],
    queryFn: () => listarAdminCiudadesApi(query),
    staleTime: 30_000,
  });
}

export function useCrearAdminCiudad() {
  const qc = useQueryClient();
  return useMutation<AdminCiudadFormResponse, Error, AdminCiudadFormPayload>({
    mutationFn: (payload) => crearAdminCiudadApi(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useActualizarAdminCiudad() {
  const qc = useQueryClient();
  return useMutation<AdminCiudadFormResponse, Error, { cid: number; payload: AdminCiudadFormPayload }>({
    mutationFn: ({ cid, payload }) => actualizarAdminCiudadApi(cid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}

export function useEliminarAdminCiudad() {
  const qc = useQueryClient();
  return useMutation<{ ok: boolean }, Error, number>({
    mutationFn: (cid) => eliminarAdminCiudadApi(cid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}
