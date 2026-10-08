import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminArlApi } from './apiAdminArl';
import type {
  AdminArlFormPayload,
  AdminArlFormResponse,
  AdminArlListQuery,
  AdminArlListResponse,
} from './types';

const QK_LIST = 'admin-arl-list' as const;

export function injectAdminArlList(query: () => AdminArlListQuery) {
  const api = inject(AdminArlApi);
  return injectQuery<AdminArlListResponse>(() => {
    const q: AdminArlListQuery = query();
    return {
      queryKey: [QK_LIST, q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectCrearAdminArl() {
  const api = inject(AdminArlApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminArlFormResponse, Error, AdminArlFormPayload>(() => ({
    mutationFn: (payload) => api.crear(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectActualizarAdminArl() {
  const api = inject(AdminArlApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminArlFormResponse, Error, { tid: number; payload: AdminArlFormPayload }>(() => ({
    mutationFn: ({ tid, payload }) => api.actualizar(tid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectEliminarAdminArl() {
  const api = inject(AdminArlApi);
  const qc = inject(QueryClient);
  return injectMutation<{ ok: boolean }, Error, number>(() => ({
    mutationFn: (tid) => api.eliminar(tid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}
