import { apiClient } from '../../../shared/api/client';
import type {
  ReporteParams,
  ReportePreviewParams,
  ReportePreviewResponse,
} from './types';

export async function generarReporteApi(params: ReporteParams): Promise<{ blob: Blob; filename: string }> {
  const body: Record<string, unknown> = { tipo: params.tipo, programa: params.programa ?? 1 };
  if (params.subprograma) body.subprograma = params.subprograma;
  if (params.fecha_inicio) body.fecha_inicio = params.fecha_inicio;
  if (params.fecha_fin) body.fecha_fin = params.fecha_fin;
  if (params.cedula) body.cedula = params.cedula;
  if (params.estado !== undefined && params.estado !== null) body.estado = params.estado;

  const response = await apiClient.post('/reportes/generar', body, { responseType: 'blob' });
  const disposition: string = (response.headers['content-disposition'] as string | undefined) ?? '';
  const match = /filename\*?=(?:UTF-8'')?([^;]+)/i.exec(disposition);
  const filename: string = match ? decodeURIComponent(match[1].replace(/^"|"$/g, '')) : 'reporte.xlsx';
  return { blob: response.data as Blob, filename };
}

export async function previewReporteApi(params: ReportePreviewParams): Promise<ReportePreviewResponse> {
  const body: Record<string, unknown> = {
    tipo: params.tipo,
    programa: params.programa ?? 1,
    page: params.page,
    page_size: params.page_size,
  };
  if (params.subprograma) body.subprograma = params.subprograma;
  if (params.fecha_inicio) body.fecha_inicio = params.fecha_inicio;
  if (params.fecha_fin) body.fecha_fin = params.fecha_fin;
  if (params.cedula) body.cedula = params.cedula;
  if (params.estado !== undefined && params.estado !== null) body.estado = params.estado;

  const response = await apiClient.post<ReportePreviewResponse>('/reportes/preview', body);
  return response.data;
}
