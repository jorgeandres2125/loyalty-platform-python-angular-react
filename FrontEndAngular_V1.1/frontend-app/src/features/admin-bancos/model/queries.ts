import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminBancosApi } from './apiAdminBancos';
import type {
  AdminBancoFormPayload,
  AdminBancoFormResponse,
  AdminBancoListQuery,
  AdminBancoListResponse,
} from './types';

const QK_LIST = 'admin-bancos-list' as const;

export function injectAdminBancosList(query: () => AdminBancoListQuery) {
  const api = inject(AdminBancosApi);
  return injectQuery<AdminBancoListResponse>(() => {
    const q: AdminBancoListQuery = query();
    return {
      queryKey: [QK_LIST, q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectCrearAdminBanco() {
  const api = inject(AdminBancosApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminBancoFormResponse, Error, AdminBancoFormPayload>(() => ({
    mutationFn: (payload) => api.crear(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectActualizarAdminBanco() {
  const api = inject(AdminBancosApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminBancoFormResponse, Error, { tid: number; payload: AdminBancoFormPayload }>(() => ({
    mutationFn: ({ tid, payload }) => api.actualizar(tid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectEliminarAdminBanco() {
  const api = inject(AdminBancosApi);
  const qc = inject(QueryClient);
  return injectMutation<{ ok: boolean }, Error, number>(() => ({
    mutationFn: (tid) => api.eliminar(tid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}
