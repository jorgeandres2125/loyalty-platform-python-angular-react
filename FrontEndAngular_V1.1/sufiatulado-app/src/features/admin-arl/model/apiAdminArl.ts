import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  AdminArlFormPayload,
  AdminArlFormResponse,
  AdminArlListQuery,
  AdminArlListResponse,
} from './types';

@Injectable({ providedIn: 'root' })
export class AdminArlApi {
  private readonly api = inject(ApiClient);

  async listar(query: AdminArlListQuery): Promise<AdminArlListResponse> {
    const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
    if (query.nombre) params['nombre'] = query.nombre;
    const response = await this.api.get<AdminArlListResponse>('/admin/arl', { params });
    return response.data;
  }

  async crear(payload: AdminArlFormPayload): Promise<AdminArlFormResponse> {
    const response = await this.api.post<AdminArlFormResponse>('/admin/arl', payload);
    return response.data;
  }

  async actualizar(tid: number, payload: AdminArlFormPayload): Promise<AdminArlFormResponse> {
    const response = await this.api.put<AdminArlFormResponse>(`/admin/arl/${tid}`, payload);
    return response.data;
  }

  async eliminar(tid: number): Promise<{ ok: boolean }> {
    const response = await this.api.delete<{ ok: boolean }>(`/admin/arl/${tid}`);
    return response.data;
  }
}
