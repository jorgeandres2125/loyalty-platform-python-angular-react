import { apiClient } from '../../../shared/api/client';
import type {
  AdminDepartamentoFormPayload,
  AdminDepartamentoFormResponse,
  AdminDepartamentoListQuery,
  AdminDepartamentoListResponse,
} from './types';

export async function listarAdminDepartamentosApi(query: AdminDepartamentoListQuery): Promise<AdminDepartamentoListResponse> {
  const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
  if (query.nombre) params.nombre = query.nombre;
  const response = await apiClient.get<AdminDepartamentoListResponse>('/admin/departamentos', { params });
  return response.data;
}

export async function crearAdminDepartamentoApi(payload: AdminDepartamentoFormPayload): Promise<AdminDepartamentoFormResponse> {
  const response = await apiClient.post<AdminDepartamentoFormResponse>('/admin/departamentos', payload);
  return response.data;
}

export async function actualizarAdminDepartamentoApi(did: number, payload: AdminDepartamentoFormPayload): Promise<AdminDepartamentoFormResponse> {
  const response = await apiClient.put<AdminDepartamentoFormResponse>(`/admin/departamentos/${did}`, payload);
  return response.data;
}

export async function eliminarAdminDepartamentoApi(did: number): Promise<{ ok: boolean }> {
  const response = await apiClient.delete<{ ok: boolean }>(`/admin/departamentos/${did}`);
  return response.data;
}
