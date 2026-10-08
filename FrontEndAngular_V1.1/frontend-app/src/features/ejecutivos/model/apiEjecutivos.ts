import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  EjecutivoFormPayload,
  EjecutivoFormResponse,
  EjecutivoListQuery,
  EjecutivoListResponse,
} from './types';

@Injectable({ providedIn: 'root' })
export class EjecutivosApi {
  private readonly api = inject(ApiClient);

  async listar(query: EjecutivoListQuery): Promise<EjecutivoListResponse> {
    const params: Record<string, string | number | boolean> = {
      page: query.page,
      page_size: query.page_size,
    };
    if (query.tipo_doc) params['tipo_doc'] = query.tipo_doc;
    if (query.documento) params['documento'] = query.documento;
    if (query.perfil) params['perfil'] = query.perfil;
    if (query.estado !== undefined) params['estado'] = query.estado;
    const response = await this.api.get<EjecutivoListResponse>('/ejecutivos', { params });
    return response.data;
  }

  async obtener(id: number): Promise<EjecutivoFormResponse> {
    const response = await this.api.get<EjecutivoFormResponse>(`/ejecutivos/${id}`);
    return response.data;
  }

  async crear(payload: EjecutivoFormPayload): Promise<EjecutivoFormResponse> {
    const response = await this.api.post<EjecutivoFormResponse>('/ejecutivos', payload);
    return response.data;
  }

  async actualizar(id: number, payload: EjecutivoFormPayload): Promise<EjecutivoFormResponse> {
    const response = await this.api.put<EjecutivoFormResponse>(`/ejecutivos/${id}`, payload);
    return response.data;
  }
}
