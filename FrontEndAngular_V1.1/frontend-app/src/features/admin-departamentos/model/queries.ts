import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminDepartamentosApi } from './apiAdminDepartamentos';
import type {
  AdminDepartamentoFormPayload,
  AdminDepartamentoFormResponse,
  AdminDepartamentoListQuery,
  AdminDepartamentoListResponse,
} from './types';

const QK_LIST = 'admin-departamentos-list' as const;

export function injectAdminDepartamentosList(query: () => AdminDepartamentoListQuery) {
  const api = inject(AdminDepartamentosApi);
  return injectQuery<AdminDepartamentoListResponse>(() => {
    const q: AdminDepartamentoListQuery = query();
    return {
      queryKey: [QK_LIST, q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectCrearAdminDepartamento() {
  const api = inject(AdminDepartamentosApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminDepartamentoFormResponse, Error, AdminDepartamentoFormPayload>(() => ({
    mutationFn: (payload) => api.crear(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectActualizarAdminDepartamento() {
  const api = inject(AdminDepartamentosApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminDepartamentoFormResponse, Error, { did: number; payload: AdminDepartamentoFormPayload }>(() => ({
    mutationFn: ({ did, payload }) => api.actualizar(did, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectEliminarAdminDepartamento() {
  const api = inject(AdminDepartamentosApi);
  const qc = inject(QueryClient);
  return injectMutation<{ ok: boolean }, Error, number>(() => ({
    mutationFn: (did) => api.eliminar(did),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}
