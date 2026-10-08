import { apiClient } from '../../../shared/api/client';
import type {
  AdminEpsFormPayload,
  AdminEpsFormResponse,
  AdminEpsListQuery,
  AdminEpsListResponse,
} from './types';

export async function listarAdminEpsApi(query: AdminEpsListQuery): Promise<AdminEpsListResponse> {
  const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
  if (query.nombre) params.nombre = query.nombre;
  const response = await apiClient.get<AdminEpsListResponse>('/admin/eps', { params });
  return response.data;
}

export async function crearAdminEpsApi(payload: AdminEpsFormPayload): Promise<AdminEpsFormResponse> {
  const response = await apiClient.post<AdminEpsFormResponse>('/admin/eps', payload);
  return response.data;
}

export async function actualizarAdminEpsApi(tid: number, payload: AdminEpsFormPayload): Promise<AdminEpsFormResponse> {
  const response = await apiClient.put<AdminEpsFormResponse>(`/admin/eps/${tid}`, payload);
  return response.data;
}

export async function eliminarAdminEpsApi(tid: number): Promise<{ ok: boolean }> {
  const response = await apiClient.delete<{ ok: boolean }>(`/admin/eps/${tid}`);
  return response.data;
}
