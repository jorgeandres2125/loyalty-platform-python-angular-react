import { apiClient } from '../../../shared/api/client';
import type {
  AsesorDocumentosListResponse,
  DocumentoEditPayload,
  DocumentoEditResponse,
  DocumentoItem,
} from './types';

export async function listarAsesoresConDocumentosApi(params: {
  programa: number;
  page: number;
  page_size: number;
  cedula?: string;
  tipo_doc?: string;
}): Promise<AsesorDocumentosListResponse> {
  const response = await apiClient.get<AsesorDocumentosListResponse>('/documentos/asesores', { params });
  return response.data;
}

export async function listarDocumentosAsesorApi(numero_documento: string): Promise<DocumentoItem[]> {
  const response = await apiClient.get<DocumentoItem[]>(`/documentos/${encodeURIComponent(numero_documento)}`);
  return response.data;
}

export async function editarDocumentoApi(
  did: number,
  payload: DocumentoEditPayload,
): Promise<DocumentoEditResponse> {
  const response = await apiClient.patch<DocumentoEditResponse>(`/documentos/${did}`, payload);
  return response.data;
}

export async function eliminarDocumentoApi(did: number): Promise<void> {
  await apiClient.delete(`/documentos/${did}`);
}
