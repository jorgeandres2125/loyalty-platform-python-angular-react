import { apiClient } from '../../../shared/api/client';
import type {
  AdminAfpFormPayload,
  AdminAfpFormResponse,
  AdminAfpListQuery,
  AdminAfpListResponse,
} from './types';

export async function listarAdminAfpApi(
  query: AdminAfpListQuery,
): Promise<AdminAfpListResponse> {
  const params: Record<string, string | number> = {
    page: query.page,
    page_size: query.page_size,
  };
  if (query.nombre) params.nombre = query.nombre;
  const response = await apiClient.get<AdminAfpListResponse>('/admin/afp', { params });
  return response.data;
}

export async function obtenerAdminAfpApi(tid: number): Promise<AdminAfpFormResponse> {
  const response = await apiClient.get<AdminAfpFormResponse>(`/admin/afp/${tid}`);
  return response.data;
}

export async function crearAdminAfpApi(
  payload: AdminAfpFormPayload,
): Promise<AdminAfpFormResponse> {
  const response = await apiClient.post<AdminAfpFormResponse>('/admin/afp', payload);
  return response.data;
}

export async function actualizarAdminAfpApi(
  tid: number,
  payload: AdminAfpFormPayload,
): Promise<AdminAfpFormResponse> {
  const response = await apiClient.put<AdminAfpFormResponse>(`/admin/afp/${tid}`, payload);
  return response.data;
}

export async function eliminarAdminAfpApi(tid: number): Promise<{ ok: boolean }> {
  const response = await apiClient.delete<{ ok: boolean }>(`/admin/afp/${tid}`);
  return response.data;
}
