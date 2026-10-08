import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { PerfilSelfApi } from './apiPerfilSelf';
import type {
  DocumentoSelfItem,
  MiDashboard,
  PerfilContacto,
  PerfilEmocional,
  PerfilTributario,
} from './types';
import { injectMaxUploadBytes } from '../../config/model/uploadLimits';
import { validarTamanoArchivo } from '../../../shared/lib/archivos';

export const PERFIL_SELF_KEYS = {
  contacto: ['perfil-self', 'contacto'] as const,
  tributario: ['perfil-self', 'tributario'] as const,
  emocional: ['perfil-self', 'emocional'] as const,
  documentos: ['perfil-self', 'documentos'] as const,
  dashboard: ['perfil-self', 'dashboard'] as const,
};

export function injectMiContacto() {
  const api = inject(PerfilSelfApi);
  return injectQuery<PerfilContacto | null>(() => ({
    queryKey: PERFIL_SELF_KEYS.contacto,
    queryFn: () => api.getMiContacto(),
  }));
}

export function injectGuardarMiContacto() {
  const api = inject(PerfilSelfApi);
  const qc = inject(QueryClient);
  return injectMutation(() => ({
    mutationFn: (payload: Omit<PerfilContacto, 'numero_documento'>) => api.putMiContacto(payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: PERFIL_SELF_KEYS.contacto });
    },
  }));
}

export function injectMiTributario(enabled: () => boolean = () => true) {
  const api = inject(PerfilSelfApi);
  return injectQuery<PerfilTributario | null>(() => ({
    queryKey: PERFIL_SELF_KEYS.tributario,
    queryFn: () => api.getMiTributario(),
    enabled: enabled(),
  }));
}

export function injectGuardarMiTributario() {
  const api = inject(PerfilSelfApi);
  const qc = inject(QueryClient);
  return injectMutation(() => ({
    mutationFn: (payload: Record<string, unknown>) => api.putMiTributario(payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: PERFIL_SELF_KEYS.tributario });
    },
  }));
}

export function injectMiEmocional() {
  const api = inject(PerfilSelfApi);
  return injectQuery<PerfilEmocional | null>(() => ({
    queryKey: PERFIL_SELF_KEYS.emocional,
    queryFn: () => api.getMiEmocional(),
  }));
}

export function injectGuardarMiEmocional() {
  const api = inject(PerfilSelfApi);
  const qc = inject(QueryClient);
  return injectMutation(() => ({
    mutationFn: (payload: Record<string, unknown>) => api.putMiEmocional(payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: PERFIL_SELF_KEYS.emocional });
    },
  }));
}

export function injectMisDocumentos(enabled: () => boolean = () => true) {
  const api = inject(PerfilSelfApi);
  return injectQuery<DocumentoSelfItem[]>(() => ({
    queryKey: PERFIL_SELF_KEYS.documentos,
    queryFn: () => api.getMisDocumentos(),
    enabled: enabled(),
  }));
}

export function injectSubirMiDocumento() {
  const api = inject(PerfilSelfApi);
  const qc = inject(QueryClient);
  // AP-0137: el tamano se valida en TODA subida con el limite del backend.
  const maxBytes = injectMaxUploadBytes();
  return injectMutation(() => ({
    mutationFn: ({ tipo, file }: { tipo: number; file: File }) => {
      validarTamanoArchivo(file, maxBytes());
      return api.uploadMiDocumento(tipo, file);
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: PERFIL_SELF_KEYS.documentos });
    },
  }));
}

export function injectEliminarMiDocumento() {
  const api = inject(PerfilSelfApi);
  const qc = inject(QueryClient);
  return injectMutation(() => ({
    mutationFn: (did: number) => api.deleteMiDocumento(did),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: PERFIL_SELF_KEYS.documentos });
    },
  }));
}

export function injectMiDashboard(enabled: () => boolean = () => true) {
  const api = inject(PerfilSelfApi);
  return injectQuery<MiDashboard>(() => ({
    queryKey: PERFIL_SELF_KEYS.dashboard,
    queryFn: () => api.getMiDashboard(),
    enabled: enabled(),
  }));
}
