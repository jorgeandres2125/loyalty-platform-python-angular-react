import { apiClient } from '../../../shared/api/client';
import type {
  RolAsignableItem,
  RolDeUsuarioItem,
  UsuariosPaginaResponse,
} from './types';

export interface ListarParams {
  page: number;
  page_size: number;
  texto?: string;
}

export async function listarRolesAsignablesApi(): Promise<RolAsignableItem[]> {
  const response = await apiClient.get<RolAsignableItem[]>('/admin/asignaciones/roles');
  return response.data;
}

export async function listarUsuariosDeRolApi(
  rid: number,
  params: ListarParams,
): Promise<UsuariosPaginaResponse> {
  const response = await apiClient.get<UsuariosPaginaResponse>(
    `/admin/asignaciones/roles/${rid}/usuarios`,
    { params },
  );
  return response.data;
}

export async function buscarUsuariosApi(params: ListarParams): Promise<UsuariosPaginaResponse> {
  const response = await apiClient.get<UsuariosPaginaResponse>('/admin/asignaciones/usuarios', {
    params,
  });
  return response.data;
}

export async function obtenerRolesDeUsuarioApi(uid: number): Promise<RolDeUsuarioItem[]> {
  const response = await apiClient.get<RolDeUsuarioItem[]>(
    `/admin/asignaciones/usuarios/${uid}/roles`,
  );
  return response.data;
}

export async function asignarRolApi(uid: number, rid: number): Promise<void> {
  await apiClient.put(`/admin/asignaciones/usuarios/${uid}/roles/${rid}`);
}

export async function quitarRolApi(uid: number, rid: number): Promise<void> {
  await apiClient.delete(`/admin/asignaciones/usuarios/${uid}/roles/${rid}`);
}