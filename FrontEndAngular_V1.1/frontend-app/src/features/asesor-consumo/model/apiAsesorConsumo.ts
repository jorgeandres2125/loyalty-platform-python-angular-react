import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type { Subprograma } from '../../../shared/api/catalogos';
import type { AsesorConsumoDetalle, AsesorConsumoFiltros, AsesorConsumoListResponse } from './types';

@Injectable({ providedIn: 'root' })
export class AsesorConsumoApi {
  private readonly api = inject(ApiClient);

  async getList(page: number, size: number, filtros?: AsesorConsumoFiltros): Promise<AsesorConsumoListResponse> {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    if (filtros?.tipo_doc) params.set('tipo_doc', filtros.tipo_doc);
    if (filtros?.documento) params.set('documento', filtros.documento);
    const { data } = await this.api.get<AsesorConsumoListResponse>(`/asesor-consumo?${params}`);
    return data;
  }

  async verificar(documento: string): Promise<{ registrado: boolean; estado: number | null }> {
    const { data } = await this.api.get<{ registrado: boolean; estado: number | null }>(
      `/asesor-consumo/verificar/${documento}`,
    );
    return data;
  }

  async getDetalle(documento: string): Promise<AsesorConsumoDetalle> {
    const { data } = await this.api.get<AsesorConsumoDetalle>(`/asesor-consumo/${documento}`);
    return data;
  }

  async getSubprogramas(cpid: number): Promise<Subprograma[]> {
    const { data } = await this.api.get<Subprograma[]>(`/asesor-consumo/subprogramas/${cpid}`);
    return data;
  }

  async postWizardPaso1(payload: object): Promise<{ numero_documento: string; estado: number }> {
    const { data } = await this.api.post<{ numero_documento: string; estado: number }>(
      '/asesor-consumo/wizard/paso1',
      payload,
    );
    return data;
  }

  async postWizardPaso3(payload: object): Promise<{ numero_documento: string }> {
    const { data } = await this.api.post<{ numero_documento: string }>(
      '/asesor-consumo/wizard/paso3',
      payload,
    );
    return data;
  }

  async finalizar(documento: string): Promise<{ numero_documento: string; estado: number }> {
    const { data } = await this.api.post<{ numero_documento: string; estado: number }>(
      `/asesor-consumo/wizard/finalizar/${documento}`,
    );
    return data;
  }
}
