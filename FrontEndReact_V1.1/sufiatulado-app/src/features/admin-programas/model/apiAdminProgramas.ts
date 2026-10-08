import { apiClient } from '../../../shared/api/client';
import type { AdminProgramaFormPayload, AdminProgramaItem } from './types';

export async function listarAdminProgramasApi(): Promise<AdminProgramaItem[]> {
  const response = await apiClient.get<AdminProgramaItem[]>('/admin/programas');
  return response.data;
}

export async function actualizarAdminProgramaApi(cpid: number, payload: AdminProgramaFormPayload): Promise<AdminProgramaItem> {
  const response = await apiClient.put<AdminProgramaItem>(`/admin/programas/${cpid}`, payload);
  return response.data;
}
