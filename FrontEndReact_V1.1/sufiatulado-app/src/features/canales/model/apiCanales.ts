import { apiClient } from '../../../shared/api/client';
import type {
  CanalActivaItem,
  CanalFormPayload,
  CanalFormResponse,
  CanalListQuery,
  CanalListResponse,
} from './types';

export async function listarCanalesActivasApi(): Promise<CanalActivaItem[]> {
  const response = await apiClient.get<CanalActivaItem[]>('/canales/activas');
  return response.data;
}

export async function listarCanalesApi(
  query: CanalListQuery,
): Promise<CanalListResponse> {
  const params: Record<string, string | number | boolean> = {
    page: query.page,
    page_size: query.page_size,
  };
  if (query.nombre) params.nombre = query.nombre;
  if (query.ind_activo !== undefined) params.ind_activo = query.ind_activo;
  const response = await apiClient.get<CanalListResponse>('/canales', { params });
  return response.data;
}

export async function obtenerCanalApi(codCanales: number): Promise<CanalFormResponse> {
  const response = await apiClient.get<CanalFormResponse>(`/canales/${codCanales}`);
  return response.data;
}

export async function crearCanalApi(
  payload: CanalFormPayload,
): Promise<CanalFormResponse> {
  const response = await apiClient.post<CanalFormResponse>('/canales', payload);
  return response.data;
}

export async function actualizarCanalApi(
  codCanales: number,
  payload: CanalFormPayload,
): Promise<CanalFormResponse> {
  const response = await apiClient.put<CanalFormResponse>(`/canales/${codCanales}`, payload);
  return response.data;
}
