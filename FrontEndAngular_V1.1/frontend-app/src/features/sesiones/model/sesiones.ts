import { Injectable, inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../../shared/api/client';
import type { SesionActiva } from './types';

const QK_SESIONES = 'sesiones-activas' as const;

@Injectable({ providedIn: 'root' })
export class SesionesApi {
  private readonly api = inject(ApiClient);

  async listarMisSesiones(): Promise<SesionActiva[]> {
    const response = await this.api.get<SesionActiva[]>('/me/sesiones');
    return response.data;
  }

  async cerrarSesion(sid: string): Promise<void> {
    await this.api.delete(`/me/sesiones/${encodeURIComponent(sid)}`);
  }

  async cerrarOtrasSesiones(): Promise<void> {
    await this.api.post('/me/sesiones/cerrar-otras');
  }
}

// AP-0130: sesiones concurrentes propias (informar + cierre remoto).
export function injectMisSesiones() {
  const api = inject(SesionesApi);
  return injectQuery<SesionActiva[]>(() => ({
    queryKey: [QK_SESIONES],
    queryFn: () => api.listarMisSesiones(),
    staleTime: 15_000,
  }));
}

export function injectCerrarSesion() {
  const api = inject(SesionesApi);
  const qc = inject(QueryClient);
  return injectMutation<void, Error, string>(() => ({
    mutationFn: (sid) => api.cerrarSesion(sid),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: [QK_SESIONES] });
    },
  }));
}

export function injectCerrarOtrasSesiones() {
  const api = inject(SesionesApi);
  const qc = inject(QueryClient);
  return injectMutation<void, Error, void>(() => ({
    mutationFn: () => api.cerrarOtrasSesiones(),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: [QK_SESIONES] });
    },
  }));
}
