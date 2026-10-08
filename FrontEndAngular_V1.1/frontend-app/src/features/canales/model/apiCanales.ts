import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  CanalActivaItem,
  CanalFormPayload,
  CanalFormResponse,
  CanalListQuery,
  CanalListResponse,
} from './types';

@Injectable({ providedIn: 'root' })
export class CanalesApi {
  private readonly api = inject(ApiClient);

  async listarActivas(): Promise<CanalActivaItem[]> {
    const response = await this.api.get<CanalActivaItem[]>('/canales/activas');
    return response.data;
  }

  async listar(query: CanalListQuery): Promise<CanalListResponse> {
    const params: Record<string, string | number | boolean> = {
      page: query.page,
      page_size: query.page_size,
    };
    if (query.nombre) params['nombre'] = query.nombre;
    if (query.ind_activo !== undefined) params['ind_activo'] = query.ind_activo;
    const response = await this.api.get<CanalListResponse>('/canales', { params });
    return response.data;
  }

  async obtener(codCanales: number): Promise<CanalFormResponse> {
    const response = await this.api.get<CanalFormResponse>(`/canales/${codCanales}`);
    return response.data;
  }

  async crear(payload: CanalFormPayload): Promise<CanalFormResponse> {
    const response = await this.api.post<CanalFormResponse>('/canales', payload);
    return response.data;
  }

  async actualizar(codCanales: number, payload: CanalFormPayload): Promise<CanalFormResponse> {
    const response = await this.api.put<CanalFormResponse>(`/canales/${codCanales}`, payload);
    return response.data;
  }
}
