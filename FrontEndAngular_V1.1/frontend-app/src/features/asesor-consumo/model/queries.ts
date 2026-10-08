import { inject } from '@angular/core';
import { injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import type { AsesorConsumoFiltros } from './types';
import { AsesorConsumoApi } from './apiAsesorConsumo';

export function injectAsesorConsumoList(
  page: () => number,
  size: () => number,
  filtros?: () => AsesorConsumoFiltros | undefined,
) {
  const api = inject(AsesorConsumoApi);
  return injectQuery(() => {
    const p = page();
    const s = size();
    const f = filtros?.();
    return {
      queryKey: ['asesor-consumo-list', p, s, f],
      queryFn: () => api.getList(p, s, f),
    };
  });
}

export function injectVerificarAsesorConsumo(documento: () => string) {
  const api = inject(AsesorConsumoApi);
  return injectQuery(() => {
    const d = documento();
    return {
      queryKey: ['asesor-consumo-verificar', d],
      queryFn: () => api.verificar(d),
      enabled: d.length >= 5 && /^\d+$/.test(d),
      retry: false,
    };
  });
}

export function injectDetalleAsesorConsumo(documento: () => string | null) {
  const api = inject(AsesorConsumoApi);
  return injectQuery(() => {
    const d = documento();
    return {
      queryKey: ['asesor-consumo-detalle', d],
      queryFn: () => api.getDetalle(d as string),
      enabled: !!d && d.length >= 3,
    };
  });
}

export function injectSubprogramasConsumo(cpid: () => number) {
  const api = inject(AsesorConsumoApi);
  return injectQuery(() => {
    const c = cpid();
    return {
      queryKey: ['asesor-consumo-subprogramas', c],
      queryFn: () => api.getSubprogramas(c),
      enabled: c > 0,
    };
  });
}

export function injectWizardPaso1Consumo() {
  const api = inject(AsesorConsumoApi);
  return injectMutation(() => ({ mutationFn: (payload: object) => api.postWizardPaso1(payload) }));
}

export function injectWizardPaso3Consumo() {
  const api = inject(AsesorConsumoApi);
  return injectMutation(() => ({ mutationFn: (payload: object) => api.postWizardPaso3(payload) }));
}

export function injectFinalizarConsumo() {
  const api = inject(AsesorConsumoApi);
  return injectMutation(() => ({ mutationFn: (documento: string) => api.finalizar(documento) }));
}
