import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type { Subprograma } from '../../../shared/api/catalogos';
import type {
  AsesorMovilidadDetalle,
  AsesorMovilidadFiltros,
  AsesorMovilidadListResponse,
  DocumentoAsesor,
} from './types';

@Injectable({ providedIn: 'root' })
export class AsesorMovilidadApi {
  private readonly api = inject(ApiClient);

  async getList(page: number, size: number, filtros?: AsesorMovilidadFiltros): Promise<AsesorMovilidadListResponse> {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    if (filtros?.tipo_doc) params.set('tipo_doc', filtros.tipo_doc);
    if (filtros?.documento) params.set('documento', filtros.documento);
    const { data } = await this.api.get<AsesorMovilidadListResponse>(`/asesor-movilidad?${params}`);
    return data;
  }

  async verificar(documento: string): Promise<{ registrado: boolean; estado: number | null }> {
    const { data } = await this.api.get<{ registrado: boolean; estado: number | null }>(
      `/asesor-movilidad/verificar/${documento}`,
    );
    return data;
  }

  async getDetalle(documento: string): Promise<AsesorMovilidadDetalle> {
    const { data } = await this.api.get<AsesorMovilidadDetalle>(`/asesor-movilidad/${documento}`);
    return data;
  }

  async getSubprogramas(cpid: number): Promise<Subprograma[]> {
    const { data } = await this.api.get<Subprograma[]>(`/asesor-movilidad/subprogramas/${cpid}`);
    return data;
  }

  async postWizardPaso1(payload: object): Promise<{ numero_documento: string; estado: number }> {
    const { data } = await this.api.post<{ numero_documento: string; estado: number }>(
      '/asesor-movilidad/wizard/paso1',
      payload,
    );
    return data;
  }

  async postWizardPaso2(payload: object): Promise<{ numero_documento: string }> {
    const { data } = await this.api.post<{ numero_documento: string }>(
      '/asesor-movilidad/wizard/paso2',
      payload,
    );
    return data;
  }

  async postWizardPaso3(payload: object): Promise<{ numero_documento: string }> {
    const { data } = await this.api.post<{ numero_documento: string }>(
      '/asesor-movilidad/wizard/paso3',
      payload,
    );
    return data;
  }

  async finalizar(documento: string): Promise<{ numero_documento: string; estado: number }> {
    const { data } = await this.api.post<{ numero_documento: string; estado: number }>(
      `/asesor-movilidad/wizard/finalizar/${documento}`,
    );
    return data;
  }

  async getDocumentos(documento: string): Promise<DocumentoAsesor[]> {
    const { data } = await this.api.get<DocumentoAsesor[]>(`/documentos/${documento}`);
    return data;
  }

  async subirDocumento(payload: { numero_documento: string; tipo: number; nombre: string }): Promise<{ did: number; estado: string }> {
    const { data } = await this.api.post<{ did: number; estado: string }>('/documentos', payload);
    return data;
  }

  async eliminarDocumento(did: number): Promise<{ ok: boolean }> {
    const { data } = await this.api.delete<{ ok: boolean }>(`/documentos/${did}`);
    return data;
  }
}
