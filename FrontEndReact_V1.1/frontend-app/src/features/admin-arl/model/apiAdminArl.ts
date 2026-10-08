import { apiClient } from '../../../shared/api/client';
import type {
  AdminArlFormPayload,
  AdminArlFormResponse,
  AdminArlListQuery,
  AdminArlListResponse,
} from './types';

export async function listarAdminArlApi(
  query: AdminArlListQuery,
): Promise<AdminArlListResponse> {
  const params: Record<string, string | number> = {
    page: query.page,
    page_size: query.page_size,
  };
  if (query.nombre) params.nombre = query.nombre;
  const response = await apiClient.get<AdminArlListResponse>('/admin/arl', { params });
  return response.data;
}

export async function crearAdminArlApi(
  payload: AdminArlFormPayload,
): Promise<AdminArlFormResponse> {
  const response = await apiClient.post<AdminArlFormResponse>('/admin/arl', payload);
  return response.data;
}

export async function actualizarAdminArlApi(
  tid: number,
  payload: AdminArlFormPayload,
): Promise<AdminArlFormResponse> {
  const response = await apiClient.put<AdminArlFormResponse>(`/admin/arl/${tid}`, payload);
  return response.data;
}

export async function eliminarAdminArlApi(tid: number): Promise<{ ok: boolean }> {
  const response = await apiClient.delete<{ ok: boolean }>(`/admin/arl/${tid}`);
  return response.data;
}
