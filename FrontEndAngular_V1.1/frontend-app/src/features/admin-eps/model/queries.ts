import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminEpsApi } from './apiAdminEps';
import type {
  AdminEpsFormPayload,
  AdminEpsFormResponse,
  AdminEpsListQuery,
  AdminEpsListResponse,
} from './types';

const QK_LIST = 'admin-eps-list' as const;

export function injectAdminEpsList(query: () => AdminEpsListQuery) {
  const api = inject(AdminEpsApi);
  return injectQuery<AdminEpsListResponse>(() => {
    const q: AdminEpsListQuery = query();
    return {
      queryKey: [QK_LIST, q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectCrearAdminEps() {
  const api = inject(AdminEpsApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminEpsFormResponse, Error, AdminEpsFormPayload>(() => ({
    mutationFn: (payload) => api.crear(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectActualizarAdminEps() {
  const api = inject(AdminEpsApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminEpsFormResponse, Error, { tid: number; payload: AdminEpsFormPayload }>(() => ({
    mutationFn: ({ tid, payload }) => api.actualizar(tid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectEliminarAdminEps() {
  const api = inject(AdminEpsApi);
  const qc = inject(QueryClient);
  return injectMutation<{ ok: boolean }, Error, number>(() => ({
    mutationFn: (tid) => api.eliminar(tid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}
