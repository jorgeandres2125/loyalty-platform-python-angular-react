import { apiClient } from '../../../shared/api/client';
import type {
  AdminProfesionFormPayload,
  AdminProfesionFormResponse,
  AdminProfesionListQuery,
  AdminProfesionListResponse,
} from './types';

export async function listarAdminProfesionesApi(query: AdminProfesionListQuery): Promise<AdminProfesionListResponse> {
  const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
  if (query.nombre) params.nombre = query.nombre;
  const response = await apiClient.get<AdminProfesionListResponse>('/admin/profesiones', { params });
  return response.data;
}

export async function crearAdminProfesionApi(payload: AdminProfesionFormPayload): Promise<AdminProfesionFormResponse> {
  const response = await apiClient.post<AdminProfesionFormResponse>('/admin/profesiones', payload);
  return response.data;
}

export async function actualizarAdminProfesionApi(tid: number, payload: AdminProfesionFormPayload): Promise<AdminProfesionFormResponse> {
  const response = await apiClient.put<AdminProfesionFormResponse>(`/admin/profesiones/${tid}`, payload);
  return response.data;
}

export async function eliminarAdminProfesionApi(tid: number): Promise<{ ok: boolean }> {
  const response = await apiClient.delete<{ ok: boolean }>(`/admin/profesiones/${tid}`);
  return response.data;
}
