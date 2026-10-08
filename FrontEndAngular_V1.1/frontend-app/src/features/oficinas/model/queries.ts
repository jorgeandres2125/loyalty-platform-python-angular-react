import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { OficinasApi } from './apiOficinas';
import type {
  OficinaActivaItem,
  OficinaFormPayload,
  OficinaFormResponse,
  OficinaListQuery,
  OficinaListResponse,
} from './types';

export function injectOficinas(query: () => OficinaListQuery) {
  const api = inject(OficinasApi);
  return injectQuery<OficinaListResponse>(() => {
    const q = query();
    return {
      queryKey: ['oficinas', q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectOficinasActivas() {
  const api = inject(OficinasApi);
  return injectQuery<OficinaActivaItem[]>(() => ({
    queryKey: ['oficinas-activas'],
    queryFn: () => api.listarActivas(),
    staleTime: 5 * 60_000,
  }));
}

export function injectOficina(codOficinas: () => number | null) {
  const api = inject(OficinasApi);
  return injectQuery<OficinaFormResponse>(() => {
    const cod = codOficinas();
    return {
      queryKey: ['oficina', cod],
      queryFn: () => api.obtener(cod ?? 0),
      enabled: cod !== null && cod > 0,
      staleTime: 15_000,
    };
  });
}

export function injectCrearOficina() {
  const api = inject(OficinasApi);
  const qc = inject(QueryClient);
  return injectMutation<OficinaFormResponse, Error, OficinaFormPayload>(() => ({
    mutationFn: (payload) => api.crear(payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['oficinas'] });
    },
  }));
}

export function injectActualizarOficina() {
  const api = inject(OficinasApi);
  const qc = inject(QueryClient);
  return injectMutation<OficinaFormResponse, Error, { codOficinas: number; payload: OficinaFormPayload }>(
    () => ({
      mutationFn: ({ codOficinas, payload }) => api.actualizar(codOficinas, payload),
      onSuccess: (data) => {
        void qc.invalidateQueries({ queryKey: ['oficinas'] });
        void qc.invalidateQueries({ queryKey: ['oficina', data.cod_oficinas] });
      },
    }),
  );
}
