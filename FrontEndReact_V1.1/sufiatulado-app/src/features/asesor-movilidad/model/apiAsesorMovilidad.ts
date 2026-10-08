import { apiClient } from '../../../shared/api/client';
import type { Subprograma } from '../../../shared/api/catalogos';
import type {
  AsesorMovilidadListResponse,
  AsesorMovilidadDetalle,
  AsesorMovilidadFiltros,
  DocumentoAsesor,
} from './types';

export async function getAsesorMovilidadListApi(page: number, size: number, filtros?: AsesorMovilidadFiltros): Promise<AsesorMovilidadListResponse> {
  const params = new URLSearchParams({ page: String(page), size: String(size) });
  if (filtros?.tipo_doc) params.set('tipo_doc', filtros.tipo_doc);
  if (filtros?.documento) params.set('documento', filtros.documento);
  const { data } = await apiClient.get<AsesorMovilidadListResponse>(`/asesor-movilidad?${params}`);
  return data;
}

export async function verificarAsesorMovilidadApi(documento: string) {
  const { data } = await apiClient.get<{ registrado: boolean; estado: number | null }>(
    `/asesor-movilidad/verificar/${documento}`,
  );
  return data;
}

export async function getDetalleAsesorMovilidadApi(documento: string): Promise<AsesorMovilidadDetalle> {
  const { data } = await apiClient.get<AsesorMovilidadDetalle>(`/asesor-movilidad/${documento}`);
  return data;
}

export async function getSubprogramasMovilidadApi(cpid: number): Promise<Subprograma[]> {
  const { data } = await apiClient.get<Subprograma[]>(`/asesor-movilidad/subprogramas/${cpid}`);
  return data;
}

export async function postWizardPaso1MovilidadApi(payload: object) {
  const { data } = await apiClient.post<{ numero_documento: string; estado: number }>(
    '/asesor-movilidad/wizard/paso1',
    payload,
  );
  return data;
}

export async function postWizardPaso2MovilidadApi(payload: object) {
  const { data } = await apiClient.post<{ numero_documento: string }>(
    '/asesor-movilidad/wizard/paso2',
    payload,
  );
  return data;
}

export async function postWizardPaso3MovilidadApi(payload: object) {
  const { data } = await apiClient.post<{ numero_documento: string }>(
    '/asesor-movilidad/wizard/paso3',
    payload,
  );
  return data;
}

export async function finalizarMovilidadApi(documento: string) {
  const { data } = await apiClient.post<{ numero_documento: string; estado: number }>(
    `/asesor-movilidad/wizard/finalizar/${documento}`,
  );
  return data;
}

export async function getDocumentosAsesorApi(documento: string): Promise<DocumentoAsesor[]> {
  const { data } = await apiClient.get<DocumentoAsesor[]>(`/documentos/${documento}`);
  return data;
}

export async function subirDocumentoMovilidadApi(payload: { numero_documento: string; tipo: number; nombre: string }) {
  const { data } = await apiClient.post<{ did: number; estado: string }>('/documentos', payload);
  return data;
}

export async function eliminarDocumentoMovilidadApi(did: number) {
  const { data } = await apiClient.delete<{ ok: boolean }>(`/documentos/${did}`);
  return data;
}
