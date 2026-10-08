import { apiClient } from '../../../shared/api/client';
import type {
  AdminCiudadFormPayload,
  AdminCiudadFormResponse,
  AdminCiudadListQuery,
  AdminCiudadListResponse,
} from './types';

export async function listarAdminCiudadesApi(query: AdminCiudadListQuery): Promise<AdminCiudadListResponse> {
  const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
  if (query.nombre) params.nombre = query.nombre;
  if (query.did !== undefined) params.did = query.did;
  const response = await apiClient.get<AdminCiudadListResponse>('/admin/ciudades', { params });
  return response.data;
}

export async function crearAdminCiudadApi(payload: AdminCiudadFormPayload): Promise<AdminCiudadFormResponse> {
  const response = await apiClient.post<AdminCiudadFormResponse>('/admin/ciudades', payload);
  return response.data;
}

export async function actualizarAdminCiudadApi(cid: number, payload: AdminCiudadFormPayload): Promise<AdminCiudadFormResponse> {
  const response = await apiClient.put<AdminCiudadFormResponse>(`/admin/ciudades/${cid}`, payload);
  return response.data;
}

export async function eliminarAdminCiudadApi(cid: number): Promise<{ ok: boolean }> {
  const response = await apiClient.delete<{ ok: boolean }>(`/admin/ciudades/${cid}`);
  return response.data;
}
