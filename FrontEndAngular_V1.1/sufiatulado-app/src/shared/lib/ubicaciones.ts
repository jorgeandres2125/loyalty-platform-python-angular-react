import { inject } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../api/client';

export interface Departamento {
  did: number;
  pid: number;
  departamento: string;
}

export interface Ciudad {
  cid: number;
  did: number;
  ciudad: string;
}

export function injectDepartamentosCompartidos() {
  const api = inject(ApiClient);
  return injectQuery(() => ({
    queryKey: ['departamentos'],
    queryFn: async (): Promise<Departamento[]> =>
      (await api.get<Departamento[]>('/ubicaciones/departamentos')).data,
    staleTime: Infinity,
  }));
}

export function injectCiudadesCompartidas(departamentoId: () => number | null) {
  const api = inject(ApiClient);
  return injectQuery(() => {
    const did = departamentoId();
    return {
      queryKey: ['ciudades', did],
      queryFn: async (): Promise<Ciudad[]> =>
        (await api.get<Ciudad[]>(`/ubicaciones/ciudades/${did}`)).data,
      enabled: did !== null,
      staleTime: Infinity,
    };
  });
}
