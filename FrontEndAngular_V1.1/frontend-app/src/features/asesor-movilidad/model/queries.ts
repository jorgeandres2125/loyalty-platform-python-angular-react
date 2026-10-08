import { inject } from '@angular/core';
import { injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import type { AsesorMovilidadFiltros } from './types';
import { AsesorMovilidadApi } from './apiAsesorMovilidad';

export function injectAsesorMovilidadList(
  page: () => number,
  size: () => number,
  filtros?: () => AsesorMovilidadFiltros | undefined,
) {
  const api = inject(AsesorMovilidadApi);
  return injectQuery(() => {
    const p = page();
    const s = size();
    const f = filtros?.();
    return {
      queryKey: ['asesor-movilidad-list', p, s, f],
      queryFn: () => api.getList(p, s, f),
    };
  });
}

export function injectVerificarAsesorMovilidad(documento: () => string) {
  const api = inject(AsesorMovilidadApi);
  return injectQuery(() => {
    const d = documento();
    return {
      queryKey: ['asesor-movilidad-verificar', d],
      queryFn: () => api.verificar(d),
      enabled: d.length >= 5 && /^\d+$/.test(d),
      retry: false,
    };
  });
}

export function injectDetalleAsesorMovilidad(documento: () => string | null) {
  const api = inject(AsesorMovilidadApi);
  return injectQuery(() => {
    const d = documento();
    return {
      queryKey: ['asesor-movilidad-detalle', d],
      queryFn: () => api.getDetalle(d as string),
      enabled: !!d && d.length >= 3,
    };
  });
}

export function injectSubprogramasMovilidad(cpid: () => number) {
  const api = inject(AsesorMovilidadApi);
  return injectQuery(() => {
    const c = cpid();
    return {
      queryKey: ['asesor-movilidad-subprogramas', c],
      queryFn: () => api.getSubprogramas(c),
      enabled: c > 0,
    };
  });
}

export function injectWizardPaso1Movilidad() {
  const api = inject(AsesorMovilidadApi);
  return injectMutation(() => ({ mutationFn: (payload: object) => api.postWizardPaso1(payload) }));
}

export function injectWizardPaso2Movilidad() {
  const api = inject(AsesorMovilidadApi);
  return injectMutation(() => ({ mutationFn: (payload: object) => api.postWizardPaso2(payload) }));
}

export function injectWizardPaso3Movilidad() {
  const api = inject(AsesorMovilidadApi);
  return injectMutation(() => ({ mutationFn: (payload: object) => api.postWizardPaso3(payload) }));
}

export function injectFinalizarMovilidad() {
  const api = inject(AsesorMovilidadApi);
  return injectMutation(() => ({ mutationFn: (documento: string) => api.finalizar(documento) }));
}
