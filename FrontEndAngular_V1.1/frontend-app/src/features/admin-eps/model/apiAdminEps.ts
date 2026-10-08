import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  AdminEpsFormPayload,
  AdminEpsFormResponse,
  AdminEpsListQuery,
  AdminEpsListResponse,
} from './types';

@Injectable({ providedIn: 'root' })
export class AdminEpsApi {
  private readonly api = inject(ApiClient);

  async listar(query: AdminEpsListQuery): Promise<AdminEpsListResponse> {
    const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
    if (query.nombre) params['nombre'] = query.nombre;
    const response = await this.api.get<AdminEpsListResponse>('/admin/eps', { params });
    return response.data;
  }

  async crear(payload: AdminEpsFormPayload): Promise<AdminEpsFormResponse> {
    const response = await this.api.post<AdminEpsFormResponse>('/admin/eps', payload);
    return response.data;
  }

  async actualizar(tid: number, payload: AdminEpsFormPayload): Promise<AdminEpsFormResponse> {
    const response = await this.api.put<AdminEpsFormResponse>(`/admin/eps/${tid}`, payload);
    return response.data;
  }

  async eliminar(tid: number): Promise<{ ok: boolean }> {
    const response = await this.api.delete<{ ok: boolean }>(`/admin/eps/${tid}`);
    return response.data;
  }
}
