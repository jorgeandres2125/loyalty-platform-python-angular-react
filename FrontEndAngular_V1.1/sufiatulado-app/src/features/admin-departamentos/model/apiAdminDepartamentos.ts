import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  AdminDepartamentoFormPayload,
  AdminDepartamentoFormResponse,
  AdminDepartamentoListQuery,
  AdminDepartamentoListResponse,
} from './types';

@Injectable({ providedIn: 'root' })
export class AdminDepartamentosApi {
  private readonly api = inject(ApiClient);

  async listar(query: AdminDepartamentoListQuery): Promise<AdminDepartamentoListResponse> {
    const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
    if (query.nombre) params['nombre'] = query.nombre;
    const response = await this.api.get<AdminDepartamentoListResponse>('/admin/departamentos', { params });
    return response.data;
  }

  async crear(payload: AdminDepartamentoFormPayload): Promise<AdminDepartamentoFormResponse> {
    const response = await this.api.post<AdminDepartamentoFormResponse>('/admin/departamentos', payload);
    return response.data;
  }

  async actualizar(did: number, payload: AdminDepartamentoFormPayload): Promise<AdminDepartamentoFormResponse> {
    const response = await this.api.put<AdminDepartamentoFormResponse>(`/admin/departamentos/${did}`, payload);
    return response.data;
  }

  async eliminar(did: number): Promise<{ ok: boolean }> {
    const response = await this.api.delete<{ ok: boolean }>(`/admin/departamentos/${did}`);
    return response.data;
  }
}
