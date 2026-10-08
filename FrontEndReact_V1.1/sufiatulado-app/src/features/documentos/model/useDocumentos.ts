import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  editarDocumentoApi,
  eliminarDocumentoApi,
  listarAsesoresConDocumentosApi,
  listarDocumentosAsesorApi,
} from './apiDocumentos';
import type {
  AsesorDocumentosListResponse,
  DocumentoEditPayload,
  DocumentoEditResponse,
  DocumentoItem,
} from './types';

export function useAsesoresConDocumentos(params: {
  programa: number;
  page: number;
  page_size: number;
  cedula?: string;
  tipo_doc?: string;
}) {
  return useQuery<AsesorDocumentosListResponse>({
    queryKey: ['asesores-con-documentos', params],
    queryFn: () => listarAsesoresConDocumentosApi(params),
    staleTime: 30_000,
  });
}

export function useDocumentosAsesor(numero_documento: string | null, enabled: boolean) {
  return useQuery<DocumentoItem[]>({
    queryKey: ['documentos-asesor', numero_documento],
    queryFn: () => listarDocumentosAsesorApi(numero_documento ?? ''),
    enabled: enabled && !!numero_documento,
    staleTime: 15_000,
  });
}

export function useEditarDocumento(numero_documento: string | null) {
  const qc = useQueryClient();
  return useMutation<DocumentoEditResponse, Error, { did: number; payload: DocumentoEditPayload }>({
    mutationFn: ({ did, payload }) => editarDocumentoApi(did, payload),
    onSuccess: () => {
      if (numero_documento) {
        qc.invalidateQueries({ queryKey: ['documentos-asesor', numero_documento] });
      }
    },
  });
}

export function useEliminarDocumento(numero_documento: string | null) {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: (did: number) => eliminarDocumentoApi(did),
    onSuccess: () => {
      if (numero_documento) {
        qc.invalidateQueries({ queryKey: ['documentos-asesor', numero_documento] });
        qc.invalidateQueries({ queryKey: ['mis-documentos', numero_documento] });
      }
    },
  });
}
