import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  AdminCiudadFormPayload,
  AdminCiudadFormResponse,
  AdminCiudadListQuery,
  AdminCiudadListResponse,
} from './types';

@Injectable({ providedIn: 'root' })
export class AdminCiudadesApi {
  private readonly api = inject(ApiClient);

  async listar(query: AdminCiudadListQuery): Promise<AdminCiudadListResponse> {
    const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
    if (query.nombre) params['nombre'] = query.nombre;
    if (query.did !== undefined) params['did'] = query.did;
    const response = await this.api.get<AdminCiudadListResponse>('/admin/ciudades', { params });
    return response.data;
  }

  async crear(payload: AdminCiudadFormPayload): Promise<AdminCiudadFormResponse> {
    const response = await this.api.post<AdminCiudadFormResponse>('/admin/ciudades', payload);
    return response.data;
  }

  async actualizar(cid: number, payload: AdminCiudadFormPayload): Promise<AdminCiudadFormResponse> {
    const response = await this.api.put<AdminCiudadFormResponse>(`/admin/ciudades/${cid}`, payload);
    return response.data;
  }

  async eliminar(cid: number): Promise<{ ok: boolean }> {
    const response = await this.api.delete<{ ok: boolean }>(`/admin/ciudades/${cid}`);
    return response.data;
  }
}
