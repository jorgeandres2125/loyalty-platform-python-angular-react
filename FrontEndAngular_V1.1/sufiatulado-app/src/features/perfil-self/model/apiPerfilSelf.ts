import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import { AuthStore } from '../../../entities/user/model/authStore';
import type {
  DocumentoSelfItem,
  MiDashboard,
  PerfilContacto,
  PerfilEmocional,
  PerfilTributario,
} from './types';

// ── Endpoints "self" del propio comisionista ────────────────────────────────

@Injectable({ providedIn: 'root' })
export class PerfilSelfApi {
  private readonly api = inject(ApiClient);
  private readonly auth = inject(AuthStore);

  miDocumento(): string {
    return this.auth.user()?.username ?? '';
  }

  async getMiContacto(): Promise<PerfilContacto | null> {
    const { data } = await this.api.get<{ contacto: PerfilContacto | null }>('/me/perfil-contacto');
    return data.contacto;
  }

  async putMiContacto(payload: Omit<PerfilContacto, 'numero_documento'>): Promise<void> {
    await this.api.put('/me/perfil-contacto', { ...payload, numero_documento: this.miDocumento() });
  }

  async getMiTributario(): Promise<PerfilTributario | null> {
    const { data } = await this.api.get<{ tributario: PerfilTributario | null }>('/me/perfil-tributario');
    return data.tributario;
  }

  async putMiTributario(payload: Record<string, unknown>): Promise<void> {
    await this.api.put('/me/perfil-tributario', { ...payload, numero_documento: this.miDocumento() });
  }

  async getMiEmocional(): Promise<PerfilEmocional | null> {
    const { data } = await this.api.get<{ emocional: PerfilEmocional | null }>('/me/perfil-emocional');
    return data.emocional;
  }

  async putMiEmocional(payload: Record<string, unknown>): Promise<void> {
    await this.api.put('/me/perfil-emocional', { ...payload, numero_documento: this.miDocumento() });
  }

  async getMisDocumentos(): Promise<DocumentoSelfItem[]> {
    const { data } = await this.api.get<DocumentoSelfItem[]>('/me/documentos');
    return data;
  }

  async uploadMiDocumento(tipo: number, file: File): Promise<DocumentoSelfItem> {
    const form = new FormData();
    form.append('tipo', String(tipo));
    form.append('file', file);
    const { data } = await this.api.post<DocumentoSelfItem>('/me/documentos/upload', form);
    return data;
  }

  async deleteMiDocumento(did: number): Promise<void> {
    await this.api.delete(`/me/documentos/${did}`);
  }

  async getMiDashboard(): Promise<MiDashboard> {
    const { data } = await this.api.get<MiDashboard>('/me/dashboard');
    return data;
  }
}
