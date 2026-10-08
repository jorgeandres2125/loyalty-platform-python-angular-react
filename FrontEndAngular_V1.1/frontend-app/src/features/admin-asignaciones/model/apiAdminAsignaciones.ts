import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type { RolAsignableItem, RolDeUsuarioItem, UsuariosPaginaResponse } from './types';

export interface ListarParams {
  page: number;
  page_size: number;
  texto?: string;
}

@Injectable({ providedIn: 'root' })
export class AdminAsignacionesApi {
  private readonly api = inject(ApiClient);

  async listarRolesAsignables(): Promise<RolAsignableItem[]> {
    const response = await this.api.get<RolAsignableItem[]>('/admin/asignaciones/roles');
    return response.data;
  }

  async listarUsuariosDeRol(rid: number, params: ListarParams): Promise<UsuariosPaginaResponse> {
    const response = await this.api.get<UsuariosPaginaResponse>(
      `/admin/asignaciones/roles/${rid}/usuarios`,
      { params: { ...params } },
    );
    return response.data;
  }

  async buscarUsuarios(params: ListarParams): Promise<UsuariosPaginaResponse> {
    const response = await this.api.get<UsuariosPaginaResponse>('/admin/asignaciones/usuarios', {
      params: { ...params },
    });
    return response.data;
  }

  async obtenerRolesDeUsuario(uid: number): Promise<RolDeUsuarioItem[]> {
    const response = await this.api.get<RolDeUsuarioItem[]>(
      `/admin/asignaciones/usuarios/${uid}/roles`,
    );
    return response.data;
  }

  async asignarRol(uid: number, rid: number): Promise<void> {
    await this.api.put(`/admin/asignaciones/usuarios/${uid}/roles/${rid}`);
  }

  async quitarRol(uid: number, rid: number): Promise<void> {
    await this.api.delete(`/admin/asignaciones/usuarios/${uid}/roles/${rid}`);
  }
}
