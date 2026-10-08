import { Injectable, inject } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../../shared/api/client';
import type { CiudadItem, DepartamentoItem } from './types';

@Injectable({ providedIn: 'root' })
export class UbicacionesApi {
  private readonly api = inject(ApiClient);

  async listarDepartamentos(): Promise<DepartamentoItem[]> {
    const { data } = await this.api.get<{ did: number; pid: number; departamento: string }[]>(
      '/ubicaciones/departamentos',
    );
    return data.map((dep) => ({ did: dep.did, departamento: dep.departamento }));
  }

  async listarCiudades(did: number): Promise<CiudadItem[]> {
    const { data } = await this.api.get<CiudadItem[]>(`/ubicaciones/ciudades/${did}`);
    return data;
  }
}

export function injectDepartamentos() {
  const api = inject(UbicacionesApi);
  return injectQuery<DepartamentoItem[]>(() => ({
    queryKey: ['departamentos'],
    queryFn: () => api.listarDepartamentos(),
    staleTime: 10 * 60_000,
  }));
}

export function injectCiudades(did: () => number | null) {
  const api = inject(UbicacionesApi);
  return injectQuery<CiudadItem[]>(() => {
    const d = did();
    return {
      queryKey: ['ciudades', d],
      queryFn: () => api.listarCiudades(d as number),
      enabled: d !== null,
      staleTime: 5 * 60_000,
    };
  });
}
