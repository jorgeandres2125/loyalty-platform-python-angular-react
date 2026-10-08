import { apiClient } from '../../../shared/api/client';
import { useAuthStore } from '../../../entities/user/model/authStore';
import type {
  DocumentoSelfItem,
  MiDashboard,
  PerfilContacto,
  PerfilEmocional,
  PerfilTributario,
} from './types';

function _miDocumento(): string {
  return useAuthStore.getState().user?.username ?? '';
}

// ── Endpoints "self" del propio comisionista ────────────────────────────────

export async function getMiContacto(): Promise<PerfilContacto | null> {
  const { data } = await apiClient.get<{ contacto: PerfilContacto | null }>('/me/perfil-contacto');
  return data.contacto;
}

export async function putMiContacto(payload: Omit<PerfilContacto, 'numero_documento'>): Promise<void> {
  await apiClient.put('/me/perfil-contacto', { ...payload, numero_documento: _miDocumento() });
}

export async function getMiTributario(): Promise<PerfilTributario | null> {
  const { data } = await apiClient.get<{ tributario: PerfilTributario | null }>('/me/perfil-tributario');
  return data.tributario;
}

export async function putMiTributario(payload: Record<string, unknown>): Promise<void> {
  await apiClient.put('/me/perfil-tributario', { ...payload, numero_documento: _miDocumento() });
}

export async function getMiEmocional(): Promise<PerfilEmocional | null> {
  const { data } = await apiClient.get<{ emocional: PerfilEmocional | null }>('/me/perfil-emocional');
  return data.emocional;
}

export async function putMiEmocional(payload: Record<string, unknown>): Promise<void> {
  await apiClient.put('/me/perfil-emocional', { ...payload, numero_documento: _miDocumento() });
}

export async function getMisDocumentos(): Promise<DocumentoSelfItem[]> {
  const { data } = await apiClient.get<DocumentoSelfItem[]>('/me/documentos');
  return data;
}

export async function uploadMiDocumento(tipo: number, file: File): Promise<DocumentoSelfItem> {
  const form = new FormData();
  form.append('tipo', String(tipo));
  form.append('file', file);
  const { data } = await apiClient.post<DocumentoSelfItem>('/me/documentos/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function deleteMiDocumento(did: number): Promise<void> {
  await apiClient.delete(`/me/documentos/${did}`);
}

export async function getMiDashboard(): Promise<MiDashboard> {
  const { data } = await apiClient.get<MiDashboard>('/me/dashboard');
  return data;
}
