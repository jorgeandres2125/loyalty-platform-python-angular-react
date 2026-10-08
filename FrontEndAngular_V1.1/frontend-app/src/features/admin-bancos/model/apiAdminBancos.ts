import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  AdminBancoFormPayload,
  AdminBancoFormResponse,
  AdminBancoListQuery,
  AdminBancoListResponse,
} from './types';

@Injectable({ providedIn: 'root' })
export class AdminBancosApi {
  private readonly api = inject(ApiClient);

  async listar(query: AdminBancoListQuery): Promise<AdminBancoListResponse> {
    const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
    if (query.nombre) params['nombre'] = query.nombre;
    const response = await this.api.get<AdminBancoListResponse>('/admin/bancos', { params });
    return response.data;
  }

  async crear(payload: AdminBancoFormPayload): Promise<AdminBancoFormResponse> {
    const response = await this.api.post<AdminBancoFormResponse>('/admin/bancos', payload);
    return response.data;
  }

  async actualizar(tid: number, payload: AdminBancoFormPayload): Promise<AdminBancoFormResponse> {
    const response = await this.api.put<AdminBancoFormResponse>(`/admin/bancos/${tid}`, payload);
    return response.data;
  }

  async eliminar(tid: number): Promise<{ ok: boolean }> {
    const response = await this.api.delete<{ ok: boolean }>(`/admin/bancos/${tid}`);
    return response.data;
  }
}
