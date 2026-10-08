import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  deleteMiDocumento,
  getMiContacto,
  getMiDashboard,
  getMiEmocional,
  getMiTributario,
  getMisDocumentos,
  putMiContacto,
  putMiEmocional,
  putMiTributario,
  uploadMiDocumento,
} from './apiPerfilSelf';
import type {
  DocumentoSelfItem,
  MiDashboard,
  PerfilContacto,
  PerfilEmocional,
  PerfilTributario,
} from './types';
import { useMaxUploadBytes } from '../../config/model/useUploadLimits';
import { validarTamanoArchivo } from '../../../shared/lib/archivos';

const KEYS = {
  contacto: ['perfil-self', 'contacto'] as const,
  tributario: ['perfil-self', 'tributario'] as const,
  emocional: ['perfil-self', 'emocional'] as const,
  documentos: ['perfil-self', 'documentos'] as const,
  dashboard: ['perfil-self', 'dashboard'] as const,
};

export function useMiContacto() {
  return useQuery<PerfilContacto | null>({ queryKey: KEYS.contacto, queryFn: getMiContacto });
}

export function useGuardarMiContacto() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: putMiContacto,
    onSuccess: () => { qc.invalidateQueries({ queryKey: KEYS.contacto }); },
  });
}

export function useMiTributario(enabled: boolean = true) {
  return useQuery<PerfilTributario | null>({
    queryKey: KEYS.tributario,
    queryFn: getMiTributario,
    enabled,
  });
}

export function useGuardarMiTributario() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: putMiTributario,
    onSuccess: () => { qc.invalidateQueries({ queryKey: KEYS.tributario }); },
  });
}

export function useMiEmocional() {
  return useQuery<PerfilEmocional | null>({ queryKey: KEYS.emocional, queryFn: getMiEmocional });
}

export function useGuardarMiEmocional() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: putMiEmocional,
    onSuccess: () => { qc.invalidateQueries({ queryKey: KEYS.emocional }); },
  });
}

export function useMisDocumentos(enabled: boolean = true) {
  return useQuery<DocumentoSelfItem[]>({
    queryKey: KEYS.documentos,
    queryFn: getMisDocumentos,
    enabled,
  });
}

export function useSubirMiDocumento() {
  const qc = useQueryClient();
  // AP-0137: el tamano se valida en TODA subida con el limite del backend.
  const maxBytes = useMaxUploadBytes();
  return useMutation({
    mutationFn: ({ tipo, file }: { tipo: number; file: File }) => {
      validarTamanoArchivo(file, maxBytes);
      return uploadMiDocumento(tipo, file);
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: KEYS.documentos }); },
  });
}

export function useEliminarMiDocumento() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (did: number) => deleteMiDocumento(did),
    onSuccess: () => { qc.invalidateQueries({ queryKey: KEYS.documentos }); },
  });
}

export function useMiDashboard(enabled: boolean = true) {
  return useQuery<MiDashboard>({
    queryKey: KEYS.dashboard,
    queryFn: getMiDashboard,
    enabled,
  });
}
