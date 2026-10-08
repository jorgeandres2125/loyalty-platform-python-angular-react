import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { CanalesApi } from './apiCanales';
import type {
  CanalActivaItem,
  CanalFormPayload,
  CanalFormResponse,
  CanalListQuery,
  CanalListResponse,
} from './types';

export function injectCanales(query: () => CanalListQuery) {
  const api = inject(CanalesApi);
  return injectQuery<CanalListResponse>(() => {
    const q = query();
    return {
      queryKey: ['canales', q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectCanalesActivas() {
  const api = inject(CanalesApi);
  return injectQuery<CanalActivaItem[]>(() => ({
    queryKey: ['canales-activas'],
    queryFn: () => api.listarActivas(),
    staleTime: 5 * 60_000,
  }));
}

export function injectCanal(codCanales: () => number | null) {
  const api = inject(CanalesApi);
  return injectQuery<CanalFormResponse>(() => {
    const cod = codCanales();
    return {
      queryKey: ['canal', cod],
      queryFn: () => api.obtener(cod ?? 0),
      enabled: cod !== null && cod > 0,
      staleTime: 15_000,
    };
  });
}

export function injectCrearCanal() {
  const api = inject(CanalesApi);
  const qc = inject(QueryClient);
  return injectMutation<CanalFormResponse, Error, CanalFormPayload>(() => ({
    mutationFn: (payload) => api.crear(payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['canales'] });
    },
  }));
}

export function injectActualizarCanal() {
  const api = inject(CanalesApi);
  const qc = inject(QueryClient);
  return injectMutation<CanalFormResponse, Error, { codCanales: number; payload: CanalFormPayload }>(
    () => ({
      mutationFn: ({ codCanales, payload }) => api.actualizar(codCanales, payload),
      onSuccess: (data) => {
        void qc.invalidateQueries({ queryKey: ['canales'] });
        void qc.invalidateQueries({ queryKey: ['canal', data.cod_canales] });
      },
    }),
  );
}
