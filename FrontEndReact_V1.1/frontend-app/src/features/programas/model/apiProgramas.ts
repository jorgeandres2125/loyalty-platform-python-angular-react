import { apiClient } from '../../../shared/api/client';
import type { ProgramaItem, SubprogramaItem } from './types';

export async function listarProgramasApi(): Promise<ProgramaItem[]> {
  const response = await apiClient.get<ProgramaItem[]>('/referencias/programas');
  return response.data;
}

export async function listarSubprogramasApi(cpid?: number): Promise<SubprogramaItem[]> {
  const params: Record<string, number> = {};
  if (cpid !== undefined) params.cpid = cpid;
  const response = await apiClient.get<SubprogramaItem[]>('/referencias/subprogramas', { params });
  return response.data;
}
