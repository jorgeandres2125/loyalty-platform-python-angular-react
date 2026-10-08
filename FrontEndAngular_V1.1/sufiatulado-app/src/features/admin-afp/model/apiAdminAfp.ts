import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  AdminAfpFormPayload,
  AdminAfpFormResponse,
  AdminAfpListQuery,
  AdminAfpListResponse,
} from './types';

@Injectable({ providedIn: 'root' })
export class AdminAfpApi {
  private readonly api = inject(ApiClient);

  async listar(query: AdminAfpListQuery): Promise<AdminAfpListResponse> {
    const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
    if (query.nombre) params['nombre'] = query.nombre;
    const response = await this.api.get<AdminAfpListResponse>('/admin/afp', { params });
    return response.data;
  }

  async obtener(tid: number): Promise<AdminAfpFormResponse> {
    const response = await this.api.get<AdminAfpFormResponse>(`/admin/afp/${tid}`);
    return response.data;
  }

  async crear(payload: AdminAfpFormPayload): Promise<AdminAfpFormResponse> {
    const response = await this.api.post<AdminAfpFormResponse>('/admin/afp', payload);
    return response.data;
  }

  async actualizar(tid: number, payload: AdminAfpFormPayload): Promise<AdminAfpFormResponse> {
    const response = await this.api.put<AdminAfpFormResponse>(`/admin/afp/${tid}`, payload);
    return response.data;
  }

  async eliminar(tid: number): Promise<{ ok: boolean }> {
    const response = await this.api.delete<{ ok: boolean }>(`/admin/afp/${tid}`);
    return response.data;
  }
}
