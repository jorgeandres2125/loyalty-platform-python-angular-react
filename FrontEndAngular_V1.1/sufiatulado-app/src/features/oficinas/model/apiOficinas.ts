import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  OficinaActivaItem,
  OficinaFormPayload,
  OficinaFormResponse,
  OficinaListQuery,
  OficinaListResponse,
} from './types';

@Injectable({ providedIn: 'root' })
export class OficinasApi {
  private readonly api = inject(ApiClient);

  async listarActivas(): Promise<OficinaActivaItem[]> {
    const response = await this.api.get<OficinaActivaItem[]>('/oficinas/activas');
    return response.data;
  }

  async listar(query: OficinaListQuery): Promise<OficinaListResponse> {
    const params: Record<string, string | number | boolean> = {
      page: query.page,
      page_size: query.page_size,
    };
    if (query.nombre) params['nombre'] = query.nombre;
    if (query.marca) params['marca'] = query.marca;
    if (query.regional) params['regional'] = query.regional;
    if (query.ind_activo !== undefined) params['ind_activo'] = query.ind_activo;
    const response = await this.api.get<OficinaListResponse>('/oficinas', { params });
    return response.data;
  }

  async obtener(codOficinas: number): Promise<OficinaFormResponse> {
    const response = await this.api.get<OficinaFormResponse>(`/oficinas/${codOficinas}`);
    return response.data;
  }

  async crear(payload: OficinaFormPayload): Promise<OficinaFormResponse> {
    const response = await this.api.post<OficinaFormResponse>('/oficinas', payload);
    return response.data;
  }

  async actualizar(codOficinas: number, payload: OficinaFormPayload): Promise<OficinaFormResponse> {
    const response = await this.api.put<OficinaFormResponse>(`/oficinas/${codOficinas}`, payload);
    return response.data;
  }
}
