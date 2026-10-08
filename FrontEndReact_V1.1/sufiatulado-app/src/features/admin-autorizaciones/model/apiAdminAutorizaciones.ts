import { apiClient } from '../../../shared/api/client';
import type { AutorizacionFlagsPayload, AutorizacionModuloItem, RolItem } from './types';

export async function listarRolesApi(): Promise<RolItem[]> {
  const response = await apiClient.get<RolItem[]>('/admin/autorizaciones/roles');
  return response.data;
}

export async function obtenerMatrizApi(rid: number): Promise<AutorizacionModuloItem[]> {
  const response = await apiClient.get<AutorizacionModuloItem[]>(
    `/admin/autorizaciones/matriz/${rid}`,
  );
  return response.data;
}

export async function actualizarPermisosApi(
  rid: number,
  moduleId: number,
  payload: AutorizacionFlagsPayload,
): Promise<AutorizacionModuloItem> {
  const response = await apiClient.put<AutorizacionModuloItem>(
    `/admin/autorizaciones/matriz/${rid}/${moduleId}`,
    payload,
  );
  return response.data;
}

export async function actualizarModuloActivoApi(
  moduleId: number,
  activo: boolean,
): Promise<void> {
  await apiClient.patch(`/admin/autorizaciones/modulos/${moduleId}`, { activo });
}
