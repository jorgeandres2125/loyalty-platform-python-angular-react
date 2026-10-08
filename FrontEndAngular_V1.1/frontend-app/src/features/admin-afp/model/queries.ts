import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminAfpApi } from './apiAdminAfp';
import type {
  AdminAfpFormPayload,
  AdminAfpFormResponse,
  AdminAfpListQuery,
  AdminAfpListResponse,
} from './types';

const QK_LIST = 'admin-afp-list' as const;

export function injectAdminAfpList(query: () => AdminAfpListQuery) {
  const api = inject(AdminAfpApi);
  return injectQuery<AdminAfpListResponse>(() => {
    const q: AdminAfpListQuery = query();
    return {
      queryKey: [QK_LIST, q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectCrearAdminAfp() {
  const api = inject(AdminAfpApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminAfpFormResponse, Error, AdminAfpFormPayload>(() => ({
    mutationFn: (payload) => api.crear(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectActualizarAdminAfp() {
  const api = inject(AdminAfpApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminAfpFormResponse, Error, { tid: number; payload: AdminAfpFormPayload }>(() => ({
    mutationFn: ({ tid, payload }) => api.actualizar(tid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectEliminarAdminAfp() {
  const api = inject(AdminAfpApi);
  const qc = inject(QueryClient);
  return injectMutation<{ ok: boolean }, Error, number>(() => ({
    mutationFn: (tid) => api.eliminar(tid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}
