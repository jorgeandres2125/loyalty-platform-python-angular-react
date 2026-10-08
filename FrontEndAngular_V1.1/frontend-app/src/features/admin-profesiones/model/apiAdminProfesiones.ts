import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  AdminProfesionFormPayload,
  AdminProfesionFormResponse,
  AdminProfesionListQuery,
  AdminProfesionListResponse,
} from './types';

@Injectable({ providedIn: 'root' })
export class AdminProfesionesApi {
  private readonly api = inject(ApiClient);

  async listar(query: AdminProfesionListQuery): Promise<AdminProfesionListResponse> {
    const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
    if (query.nombre) params['nombre'] = query.nombre;
    const response = await this.api.get<AdminProfesionListResponse>('/admin/profesiones', { params });
    return response.data;
  }

  async crear(payload: AdminProfesionFormPayload): Promise<AdminProfesionFormResponse> {
    const response = await this.api.post<AdminProfesionFormResponse>('/admin/profesiones', payload);
    return response.data;
  }

  async actualizar(tid: number, payload: AdminProfesionFormPayload): Promise<AdminProfesionFormResponse> {
    const response = await this.api.put<AdminProfesionFormResponse>(`/admin/profesiones/${tid}`, payload);
    return response.data;
  }

  async eliminar(tid: number): Promise<{ ok: boolean }> {
    const response = await this.api.delete<{ ok: boolean }>(`/admin/profesiones/${tid}`);
    return response.data;
  }
}
