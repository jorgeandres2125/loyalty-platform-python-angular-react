import { apiClient } from '../../../shared/api/client';
import type {
  OficinaActivaItem,
  OficinaFormPayload,
  OficinaFormResponse,
  OficinaListQuery,
  OficinaListResponse,
} from './types';

export async function listarOficinasActivasApi(): Promise<OficinaActivaItem[]> {
  const response = await apiClient.get<OficinaActivaItem[]>('/oficinas/activas');
  return response.data;
}

export async function listarOficinasApi(
  query: OficinaListQuery,
): Promise<OficinaListResponse> {
  const params: Record<string, string | number | boolean> = {
    page: query.page,
    page_size: query.page_size,
  };
  if (query.nombre) params.nombre = query.nombre;
  if (query.marca) params.marca = query.marca;
  if (query.regional) params.regional = query.regional;
  if (query.ind_activo !== undefined) params.ind_activo = query.ind_activo;
  const response = await apiClient.get<OficinaListResponse>('/oficinas', { params });
  return response.data;
}

export async function obtenerOficinaApi(codOficinas: number): Promise<OficinaFormResponse> {
  const response = await apiClient.get<OficinaFormResponse>(`/oficinas/${codOficinas}`);
  return response.data;
}

export async function crearOficinaApi(
  payload: OficinaFormPayload,
): Promise<OficinaFormResponse> {
  const response = await apiClient.post<OficinaFormResponse>('/oficinas', payload);
  return response.data;
}

export async function actualizarOficinaApi(
  codOficinas: number,
  payload: OficinaFormPayload,
): Promise<OficinaFormResponse> {
  const response = await apiClient.put<OficinaFormResponse>(`/oficinas/${codOficinas}`, payload);
  return response.data;
}
