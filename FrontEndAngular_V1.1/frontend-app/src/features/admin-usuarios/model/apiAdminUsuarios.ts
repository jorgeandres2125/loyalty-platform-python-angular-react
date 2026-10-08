import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  EstadoCuentaPayload,
  PasswordTemporalResultado,
  UsuarioListItem,
  UsuarioListQuery,
  UsuarioListResponse,
} from './types';

/** Programa al que pertenece el comisionista (define la ruta de asesor). */
export type ProgramaAsesor = 'consumo' | 'movilidad';

@Injectable({ providedIn: 'root' })
export class AdminUsuariosApi {
  private readonly api = inject(ApiClient);

  async listar(query: UsuarioListQuery): Promise<UsuarioListResponse> {
    const params: Record<string, string | number | boolean> = {
      page: query.page,
      page_size: query.page_size,
    };
    if (query.texto) params['texto'] = query.texto;
    if (query.activo !== undefined) params['activo'] = query.activo;
    const response = await this.api.get<UsuarioListResponse>('/admin/usuarios', { params });
    return response.data;
  }

  /** Panel admin: habilita/deshabilita cualquier cuenta por uid. */
  async cambiarEstadoUsuario(uid: number, payload: EstadoCuentaPayload): Promise<UsuarioListItem> {
    const response = await this.api.patch<UsuarioListItem>(`/admin/usuarios/${uid}/estado`, payload);
    return response.data;
  }

  /** Pantalla de asesor: deshabilita la cuenta del comisionista por documento. */
  async cambiarEstadoComisionista(
    programa: ProgramaAsesor,
    numeroDocumento: string,
    payload: EstadoCuentaPayload,
  ): Promise<UsuarioListItem> {
    const response = await this.api.patch<UsuarioListItem>(
      `/asesor-${programa}/${encodeURIComponent(numeroDocumento)}/estado`,
      payload,
    );
    return response.data;
  }

  // AP-0047: genera una contrasena temporal para la cuenta (la clave se muestra una sola vez).
  async emitirPasswordTemporal(uid: number): Promise<PasswordTemporalResultado> {
    const response = await this.api.post<PasswordTemporalResultado>(
      `/admin/usuarios/${uid}/password-temporal`,
      {},
    );
    return response.data;
  }
}
