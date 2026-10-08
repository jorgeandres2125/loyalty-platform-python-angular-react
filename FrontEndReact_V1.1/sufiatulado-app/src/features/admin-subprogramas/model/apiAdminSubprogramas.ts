import { apiClient } from '../../../shared/api/client';
import type {
  AdminSubprogramaFormPayload,
  AdminSubprogramaFormResponse,
  AdminSubprogramaListQuery,
  AdminSubprogramaListResponse,
} from './types';

export async function listarAdminSubprogramasApi(query: AdminSubprogramaListQuery): Promise<AdminSubprogramaListResponse> {
  const params: Record<string, string | number> = { page: query.page, page_size: query.page_size };
  if (query.nombre) params.nombre = query.nombre;
  if (query.cpid !== undefined) params.cpid = query.cpid;
  const response = await apiClient.get<AdminSubprogramaListResponse>('/admin/subprogramas', { params });
  return response.data;
}

export async function crearAdminSubprogramaApi(payload: AdminSubprogramaFormPayload): Promise<AdminSubprogramaFormResponse> {
  const response = await apiClient.post<AdminSubprogramaFormResponse>('/admin/subprogramas', payload);
  return response.data;
}

export async function actualizarAdminSubprogramaApi(cspid: number, payload: AdminSubprogramaFormPayload): Promise<AdminSubprogramaFormResponse> {
  const response = await apiClient.put<AdminSubprogramaFormResponse>(`/admin/subprogramas/${cspid}`, payload);
  return response.data;
}

export async function eliminarAdminSubprogramaApi(cspid: number): Promise<{ ok: boolean }> {
  const response = await apiClient.delete<{ ok: boolean }>(`/admin/subprogramas/${cspid}`);
  return response.data;
}
