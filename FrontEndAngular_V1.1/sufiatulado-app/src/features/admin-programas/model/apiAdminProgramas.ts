import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type { AdminProgramaFormPayload, AdminProgramaItem } from './types';

@Injectable({ providedIn: 'root' })
export class AdminProgramasApi {
  private readonly api = inject(ApiClient);

  async listar(): Promise<AdminProgramaItem[]> {
    const response = await this.api.get<AdminProgramaItem[]>('/admin/programas');
    return response.data;
  }

  async actualizar(cpid: number, payload: AdminProgramaFormPayload): Promise<AdminProgramaItem> {
    const response = await this.api.put<AdminProgramaItem>(`/admin/programas/${cpid}`, payload);
    return response.data;
  }
}
