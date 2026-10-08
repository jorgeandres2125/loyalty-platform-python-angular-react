import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { EjecutivosApi } from './apiEjecutivos';
import type {
  EjecutivoFormPayload,
  EjecutivoFormResponse,
  EjecutivoListQuery,
  EjecutivoListResponse,
} from './types';

export function injectEjecutivos(query: () => EjecutivoListQuery) {
  const api = inject(EjecutivosApi);
  return injectQuery<EjecutivoListResponse>(() => {
    const q = query();
    return {
      queryKey: ['ejecutivos', q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectEjecutivo(id: () => number | null) {
  const api = inject(EjecutivosApi);
  return injectQuery<EjecutivoFormResponse>(() => {
    const i = id();
    return {
      queryKey: ['ejecutivo', i],
      queryFn: () => api.obtener(i ?? 0),
      enabled: i !== null && i > 0,
      staleTime: 15_000,
    };
  });
}

export function injectCrearEjecutivo() {
  const api = inject(EjecutivosApi);
  const qc = inject(QueryClient);
  return injectMutation<EjecutivoFormResponse, Error, EjecutivoFormPayload>(() => ({
    mutationFn: (payload) => api.crear(payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['ejecutivos'] });
    },
  }));
}

export function injectActualizarEjecutivo() {
  const api = inject(EjecutivosApi);
  const qc = inject(QueryClient);
  return injectMutation<EjecutivoFormResponse, Error, { id: number; payload: EjecutivoFormPayload }>(
    () => ({
      mutationFn: ({ id, payload }) => api.actualizar(id, payload),
      onSuccess: (data) => {
        void qc.invalidateQueries({ queryKey: ['ejecutivos'] });
        void qc.invalidateQueries({ queryKey: ['ejecutivo', data.id] });
      },
    }),
  );
}
