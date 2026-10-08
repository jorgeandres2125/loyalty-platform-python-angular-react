import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type { AutorizacionFlagsPayload, AutorizacionModuloItem, RolItem } from './types';

@Injectable({ providedIn: 'root' })
export class AdminAutorizacionesApi {
  private readonly api = inject(ApiClient);

  async listarRoles(): Promise<RolItem[]> {
    const response = await this.api.get<RolItem[]>('/admin/autorizaciones/roles');
    return response.data;
  }

  async obtenerMatriz(rid: number): Promise<AutorizacionModuloItem[]> {
    const response = await this.api.get<AutorizacionModuloItem[]>(
      `/admin/autorizaciones/matriz/${rid}`,
    );
    return response.data;
  }

  async actualizarPermisos(
    rid: number,
    moduleId: number,
    payload: AutorizacionFlagsPayload,
  ): Promise<AutorizacionModuloItem> {
    const response = await this.api.put<AutorizacionModuloItem>(
      `/admin/autorizaciones/matriz/${rid}/${moduleId}`,
      payload,
    );
    return response.data;
  }

  async actualizarModuloActivo(moduleId: number, activo: boolean): Promise<void> {
    await this.api.patch(`/admin/autorizaciones/modulos/${moduleId}`, { activo });
  }
}
