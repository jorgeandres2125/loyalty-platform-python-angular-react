import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { DocumentosApi, type AsesoresConDocumentosParams } from './apiDocumentos';
import type {
  AsesorDocumentosListResponse,
  DocumentoEditPayload,
  DocumentoEditResponse,
  DocumentoItem,
} from './types';

export function injectAsesoresConDocumentos(params: () => AsesoresConDocumentosParams) {
  const api = inject(DocumentosApi);
  return injectQuery<AsesorDocumentosListResponse>(() => {
    const p = params();
    return {
      queryKey: ['asesores-con-documentos', p],
      queryFn: () => api.listarAsesoresConDocumentos(p),
      staleTime: 30_000,
    };
  });
}

export function injectDocumentosAsesor(numero_documento: () => string | null, enabled: () => boolean) {
  const api = inject(DocumentosApi);
  return injectQuery<DocumentoItem[]>(() => {
    const doc = numero_documento();
    return {
      queryKey: ['documentos-asesor', doc],
      queryFn: () => api.listarDocumentosAsesor(doc ?? ''),
      enabled: enabled() && !!doc,
      staleTime: 15_000,
    };
  });
}

export function injectEditarDocumento(numero_documento: () => string | null) {
  const api = inject(DocumentosApi);
  const qc = inject(QueryClient);
  return injectMutation<DocumentoEditResponse, Error, { did: number; payload: DocumentoEditPayload }>(
    () => ({
      mutationFn: ({ did, payload }) => api.editarDocumento(did, payload),
      onSuccess: () => {
        const doc = numero_documento();
        if (doc) {
          void qc.invalidateQueries({ queryKey: ['documentos-asesor', doc] });
        }
      },
    }),
  );
}

export function injectEliminarDocumento(numero_documento: () => string | null) {
  const api = inject(DocumentosApi);
  const qc = inject(QueryClient);
  return injectMutation<void, Error, number>(() => ({
    mutationFn: (did: number) => api.eliminarDocumento(did),
    onSuccess: () => {
      const doc = numero_documento();
      if (doc) {
        void qc.invalidateQueries({ queryKey: ['documentos-asesor', doc] });
        void qc.invalidateQueries({ queryKey: ['mis-documentos', doc] });
      }
    },
  }));
}
