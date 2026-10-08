import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminSubprogramasApi } from './apiAdminSubprogramas';
import type {
  AdminSubprogramaFormPayload,
  AdminSubprogramaFormResponse,
  AdminSubprogramaListQuery,
  AdminSubprogramaListResponse,
} from './types';

const QK_LIST = 'admin-subprogramas-list' as const;

export function injectAdminSubprogramasList(query: () => AdminSubprogramaListQuery) {
  const api = inject(AdminSubprogramasApi);
  return injectQuery<AdminSubprogramaListResponse>(() => {
    const q: AdminSubprogramaListQuery = query();
    return {
      queryKey: [QK_LIST, q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectCrearAdminSubprograma() {
  const api = inject(AdminSubprogramasApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminSubprogramaFormResponse, Error, AdminSubprogramaFormPayload>(() => ({
    mutationFn: (payload) => api.crear(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectActualizarAdminSubprograma() {
  const api = inject(AdminSubprogramasApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminSubprogramaFormResponse, Error, { cspid: number; payload: AdminSubprogramaFormPayload }>(() => ({
    mutationFn: ({ cspid, payload }) => api.actualizar(cspid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectEliminarAdminSubprograma() {
  const api = inject(AdminSubprogramasApi);
  const qc = inject(QueryClient);
  return injectMutation<{ ok: boolean }, Error, number>(() => ({
    mutationFn: (cspid) => api.eliminar(cspid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}
