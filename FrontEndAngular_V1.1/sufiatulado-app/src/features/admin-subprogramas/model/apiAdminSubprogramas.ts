import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  AdminSubprogramaFormPayload,
  AdminSubprogramaFormResponse,
  AdminSubprogramaListQuery,
  AdminSubprogramaListResponse,
} from './types';

@Injectable({ providedIn: 'root' })
export class AdminSubprogramasApi {
  private readonly api = inject(ApiClient);

  async listar(query: AdminSubprogramaListQuery): Promise<AdminSubprogramaListResponse> {
    const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
    if (query.nombre) params['nombre'] = query.nombre;
    if (query.cpid !== undefined) params['cpid'] = query.cpid;
    const response = await this.api.get<AdminSubprogramaListResponse>('/admin/subprogramas', { params });
    return response.data;
  }

  async crear(payload: AdminSubprogramaFormPayload): Promise<AdminSubprogramaFormResponse> {
    const response = await this.api.post<AdminSubprogramaFormResponse>('/admin/subprogramas', payload);
    return response.data;
  }

  async actualizar(cspid: number, payload: AdminSubprogramaFormPayload): Promise<AdminSubprogramaFormResponse> {
    const response = await this.api.put<AdminSubprogramaFormResponse>(`/admin/subprogramas/${cspid}`, payload);
    return response.data;
  }

  async eliminar(cspid: number): Promise<{ ok: boolean }> {
    const response = await this.api.delete<{ ok: boolean }>(`/admin/subprogramas/${cspid}`);
    return response.data;
  }
}
