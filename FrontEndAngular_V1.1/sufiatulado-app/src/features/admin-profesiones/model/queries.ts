import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminProfesionesApi } from './apiAdminProfesiones';
import type {
  AdminProfesionFormPayload,
  AdminProfesionFormResponse,
  AdminProfesionListQuery,
  AdminProfesionListResponse,
} from './types';

const QK_LIST = 'admin-profesiones-list' as const;

export function injectAdminProfesionesList(query: () => AdminProfesionListQuery) {
  const api = inject(AdminProfesionesApi);
  return injectQuery<AdminProfesionListResponse>(() => {
    const q: AdminProfesionListQuery = query();
    return {
      queryKey: [QK_LIST, q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectCrearAdminProfesion() {
  const api = inject(AdminProfesionesApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminProfesionFormResponse, Error, AdminProfesionFormPayload>(() => ({
    mutationFn: (payload) => api.crear(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectActualizarAdminProfesion() {
  const api = inject(AdminProfesionesApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminProfesionFormResponse, Error, { tid: number; payload: AdminProfesionFormPayload }>(() => ({
    mutationFn: ({ tid, payload }) => api.actualizar(tid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}

export function injectEliminarAdminProfesion() {
  const api = inject(AdminProfesionesApi);
  const qc = inject(QueryClient);
  return injectMutation<{ ok: boolean }, Error, number>(() => ({
    mutationFn: (tid) => api.eliminar(tid),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  }));
}
