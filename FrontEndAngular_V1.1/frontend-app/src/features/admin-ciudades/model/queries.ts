import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminCiudadesApi } from './apiAdminCiudades';
import type {
  AdminCiudadFormPayload,
  AdminCiudadFormResponse,
  AdminCiudadListQuery,
  AdminCiudadListResponse,
} from './types';

const QK_LIST = 'admin-ciudades-list' as const;

export function injectAdminCiudadesList(query: () => AdminCiudadListQuery) {
  const api = inject(AdminCiudadesApi);
  return injectQuery<AdminCiudadListResponse>(() => {
    const q: AdminCiudadListQuery = query();
    return {
      queryKey: [QK_LIST, q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectCrearAdminCiudad() {
  const api = inject(AdminCiudadesApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminCiudadFormResponse, Error, AdminCiudadFormPayload>(() => ({
    mutationFn: (payload) => api.crear(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectActualizarAdminCiudad() {
  const api = inject(AdminCiudadesApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminCiudadFormResponse, Error, { cid: number; payload: AdminCiudadFormPayload }>(() => ({
    mutationFn: ({ cid, payload }) => api.actualizar(cid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectEliminarAdminCiudad() {
  const api = inject(AdminCiudadesApi);
  const qc = inject(QueryClient);
  return injectMutation<{ ok: boolean }, Error, number>(() => ({
    mutationFn: (cid) => api.eliminar(cid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}
