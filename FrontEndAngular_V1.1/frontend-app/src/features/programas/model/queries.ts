import { inject } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ProgramasApi } from './apiProgramas';
import type { ProgramaItem, SubprogramaItem } from './types';

export function injectProgramas() {
  const api = inject(ProgramasApi);
  return injectQuery<ProgramaItem[]>(() => ({
    queryKey: ['programas'],
    queryFn: () => api.listarProgramas(),
    staleTime: 5 * 60_000,
  }));
}

export function injectSubprogramas(cpid: () => number | undefined = () => undefined) {
  const api = inject(ProgramasApi);
  return injectQuery<SubprogramaItem[]>(() => {
    const c = cpid();
    return {
      queryKey: ['subprogramas', c ?? 'all'],
      queryFn: () => api.listarSubprogramas(c),
      staleTime: 5 * 60_000,
    };
  });
}
