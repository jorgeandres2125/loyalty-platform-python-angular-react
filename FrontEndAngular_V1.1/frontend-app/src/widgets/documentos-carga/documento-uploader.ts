import { inject } from '@angular/core';
import { ApiClient } from '../../shared/api/client';
import { validarTamanoArchivo } from '../../shared/lib/archivos';

/** Documento ya cargado que se muestra junto a la zona de carga. */
export interface DocExistente {
  did: number;
  nombre: string;
  version: number;
}

/**
 * Estrategia de carga/eliminación de documentos. Los asesores usan `/documentos/*`
 * (envían el numero_documento del comisionista) y el perfil propio `/me/documentos/*`
 * (AP-0055: el backend resuelve el dueño desde el JWT).
 */
export interface DocumentoUploader {
  subir(archivo: File, nombreArchivo: string, tipo: number, numeroDocumento: string): Promise<void>;
  eliminar(did: number): Promise<void>;
  /** Valida el tamaño antes de subir y avisa con un toast específico (pantallas de asesor). */
  prevalidarTamano: boolean;
  /** Muestra un toast de éxito tras la carga (perfil propio). */
  toastExito: boolean;
}

/** Uploader de las pantallas de asesor (staff): `/documentos/upload`. */
export function injectUploaderAsesor(): DocumentoUploader {
  const api = inject(ApiClient);
  return {
    prevalidarTamano: true,
    toastExito: false,
    subir: async (archivo, nombreArchivo, tipo, numeroDocumento) => {
      const form = new FormData();
      form.append('numero_documento', numeroDocumento);
      form.append('tipo', String(tipo));
      form.append('file', archivo, nombreArchivo);
      await api.post('/documentos/upload', form);
    },
    eliminar: async (did) => {
      await api.delete(`/documentos/${did}`);
    },
  };
}

/** Uploader del perfil propio del comisionista: `/me/documentos/upload`. */
export function injectUploaderPropio(maxBytes: () => number): DocumentoUploader {
  const api = inject(ApiClient);
  return {
    prevalidarTamano: false,
    toastExito: true,
    subir: async (archivo, nombreArchivo, tipo) => {
      const form = new FormData();
      // AP-0055: el backend resuelve el numero_documento desde el JWT; no se envia
      // desde el cliente (el dueno solo puede subir sus propios documentos).
      form.append('tipo', String(tipo));
      form.append('file', archivo, nombreArchivo);
      validarTamanoArchivo(archivo, maxBytes());
      await api.post('/me/documentos/upload', form);
    },
    eliminar: async (did) => {
      await api.delete(`/me/documentos/${did}`);
    },
  };
}

export function detalleErrorDoc(err: unknown, fallback: string): string {
  const msg = (err as { response?: { data?: { detail?: string | string[] } } })?.response?.data?.detail;
  return Array.isArray(msg) ? msg.join(' | ') : (msg ?? fallback);
}
