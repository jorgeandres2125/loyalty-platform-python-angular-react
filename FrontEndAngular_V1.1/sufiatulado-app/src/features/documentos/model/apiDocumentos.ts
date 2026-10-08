import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  AsesorDocumentosListResponse,
  DocumentoEditPayload,
  DocumentoEditResponse,
  DocumentoItem,
} from './types';

export interface AsesoresConDocumentosParams {
  programa: number;
  page: number;
  page_size: number;
  cedula?: string;
  tipo_doc?: string;
}

@Injectable({ providedIn: 'root' })
export class DocumentosApi {
  private readonly api = inject(ApiClient);

  async listarAsesoresConDocumentos(params: AsesoresConDocumentosParams): Promise<AsesorDocumentosListResponse> {
    const response = await this.api.get<AsesorDocumentosListResponse>('/documentos/asesores', {
      params: { ...params },
    });
    return response.data;
  }

  async listarDocumentosAsesor(numero_documento: string): Promise<DocumentoItem[]> {
    const response = await this.api.get<DocumentoItem[]>(
      `/documentos/${encodeURIComponent(numero_documento)}`,
    );
    return response.data;
  }

  async editarDocumento(did: number, payload: DocumentoEditPayload): Promise<DocumentoEditResponse> {
    const response = await this.api.patch<DocumentoEditResponse>(`/documentos/${did}`, payload);
    return response.data;
  }

  async eliminarDocumento(did: number): Promise<void> {
    await this.api.delete(`/documentos/${did}`);
  }
}
