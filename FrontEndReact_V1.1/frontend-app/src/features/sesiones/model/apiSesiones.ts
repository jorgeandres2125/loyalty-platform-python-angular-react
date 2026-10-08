import { apiClient } from '../../../shared/api/client';
import type { SesionActiva } from './types';

export async function listarMisSesionesApi(): Promise<SesionActiva[]> {
  const response = await apiClient.get<SesionActiva[]>('/me/sesiones');
  return response.data;
}

export async function cerrarSesionApi(sid: string): Promise<void> {
  await apiClient.delete(`/me/sesiones/${encodeURIComponent(sid)}`);
}

export async function cerrarOtrasSesionesApi(): Promise<void> {
  await apiClient.post('/me/sesiones/cerrar-otras');
}