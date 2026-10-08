import { apiClient } from '../../../shared/api/client';
import type {
  EjecutivoFormPayload,
  EjecutivoFormResponse,
  EjecutivoListQuery,
  EjecutivoListResponse,
} from './types';

export async function listarEjecutivosApi(
  query: EjecutivoListQuery,
): Promise<EjecutivoListResponse> {
  const params: Record<string, string | number | boolean> = {
    page: query.page,
    page_size: query.page_size,
  };
  if (query.tipo_doc) params.tipo_doc = query.tipo_doc;
  if (query.documento) params.documento = query.documento;
  if (query.perfil) params.perfil = query.perfil;
  if (query.estado !== undefined) params.estado = query.estado;
  const response = await apiClient.get<EjecutivoListResponse>('/ejecutivos', { params });
  return response.data;
}

export async function obtenerEjecutivoApi(id: number): Promise<EjecutivoFormResponse> {
  const response = await apiClient.get<EjecutivoFormResponse>(`/ejecutivos/${id}`);
  return response.data;
}

export async function crearEjecutivoApi(
  payload: EjecutivoFormPayload,
): Promise<EjecutivoFormResponse> {
  const response = await apiClient.post<EjecutivoFormResponse>('/ejecutivos', payload);
  return response.data;
}

export async function actualizarEjecutivoApi(
  id: number,
  payload: EjecutivoFormPayload,
): Promise<EjecutivoFormResponse> {
  const response = await apiClient.put<EjecutivoFormResponse>(`/ejecutivos/${id}`, payload);
  return response.data;
}
