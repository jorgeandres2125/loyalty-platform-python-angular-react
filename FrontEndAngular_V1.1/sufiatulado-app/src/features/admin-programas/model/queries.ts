import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminProgramasApi } from './apiAdminProgramas';
import type { AdminProgramaFormPayload, AdminProgramaItem } from './types';

const QK_LIST = 'admin-programas-list' as const;

export function injectAdminProgramasList() {
  const api = inject(AdminProgramasApi);
  return injectQuery<AdminProgramaItem[]>(() => ({
    queryKey: [QK_LIST],
    queryFn: () => api.listar(),
    staleTime: 60_000,
  }));
}

export function injectActualizarAdminPrograma() {
  const api = inject(AdminProgramasApi);
  const qc = inject(QueryClient);
  return injectMutation<AdminProgramaItem, Error, { cpid: number; payload: AdminProgramaFormPayload }>(
    () => ({
      mutationFn: ({ cpid, payload }) => api.actualizar(cpid, payload),
      onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
    }),
  );
}
