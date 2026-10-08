import { apiClient } from '../../../shared/api/client';
import type { Subprograma } from '../../../shared/api/catalogos';
import type {
  AsesorConsumoListResponse,
  AsesorConsumoDetalle,
  AsesorConsumoFiltros,
} from './types';

export async function getAsesorConsumoListApi(page: number, size: number, filtros?: AsesorConsumoFiltros): Promise<AsesorConsumoListResponse> {
  const params = new URLSearchParams({ page: String(page), size: String(size) });
  if (filtros?.tipo_doc) params.set('tipo_doc', filtros.tipo_doc);
  if (filtros?.documento) params.set('documento', filtros.documento);
  const { data } = await apiClient.get<AsesorConsumoListResponse>(`/asesor-consumo?${params}`);
  return data;
}

export async function verificarAsesorConsumoApi(documento: string) {
  const { data } = await apiClient.get<{ registrado: boolean; estado: number | null }>(
    `/asesor-consumo/verificar/${documento}`,
  );
  return data;
}

export async function getDetalleAsesorConsumoApi(documento: string): Promise<AsesorConsumoDetalle> {
  const { data } = await apiClient.get<AsesorConsumoDetalle>(`/asesor-consumo/${documento}`);
  return data;
}

export async function getSubprogramasConsumoApi(cpid: number): Promise<Subprograma[]> {
  const { data } = await apiClient.get<Subprograma[]>(`/asesor-consumo/subprogramas/${cpid}`);
  return data;
}

export async function postWizardPaso1ConsumoApi(payload: object) {
  const { data } = await apiClient.post<{ numero_documento: string; estado: number }>(
    '/asesor-consumo/wizard/paso1',
    payload,
  );
  return data;
}

export async function postWizardPaso3ConsumoApi(payload: object) {
  const { data } = await apiClient.post<{ numero_documento: string }>(
    '/asesor-consumo/wizard/paso3',
    payload,
  );
  return data;
}

export async function finalizarConsumoApi(documento: string) {
  const { data } = await apiClient.post<{ numero_documento: string; estado: number }>(
    `/asesor-consumo/wizard/finalizar/${documento}`,
  );
  return data;
}
