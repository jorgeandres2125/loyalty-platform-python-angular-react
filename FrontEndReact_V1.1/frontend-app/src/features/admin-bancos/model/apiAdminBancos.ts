import { apiClient } from '../../../shared/api/client';
import type {
  AdminBancoFormPayload,
  AdminBancoFormResponse,
  AdminBancoListQuery,
  AdminBancoListResponse,
} from './types';

export async function listarAdminBancosApi(query: AdminBancoListQuery): Promise<AdminBancoListResponse> {
  const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
  if (query.nombre) params.nombre = query.nombre;
  const response = await apiClient.get<AdminBancoListResponse>('/admin/bancos', { params });
  return response.data;
}

export async function crearAdminBancoApi(payload: AdminBancoFormPayload): Promise<AdminBancoFormResponse> {
  const response = await apiClient.post<AdminBancoFormResponse>('/admin/bancos', payload);
  return response.data;
}

export async function actualizarAdminBancoApi(tid: number, payload: AdminBancoFormPayload): Promise<AdminBancoFormResponse> {
  const response = await apiClient.put<AdminBancoFormResponse>(`/admin/bancos/${tid}`, payload);
  return response.data;
}

export async function eliminarAdminBancoApi(tid: number): Promise<{ ok: boolean }> {
  const response = await apiClient.delete<{ ok: boolean }>(`/admin/bancos/${tid}`);
  return response.data;
}
