import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type { ProgramaItem, SubprogramaItem } from './types';

@Injectable({ providedIn: 'root' })
export class ProgramasApi {
  private readonly api = inject(ApiClient);

  async listarProgramas(): Promise<ProgramaItem[]> {
    const response = await this.api.get<ProgramaItem[]>('/referencias/programas');
    return response.data;
  }

  async listarSubprogramas(cpid?: number): Promise<SubprogramaItem[]> {
    const params: Record<string, number> = {};
    if (cpid !== undefined) params['cpid'] = cpid;
    const response = await this.api.get<SubprogramaItem[]>('/referencias/subprogramas', { params });
    return response.data;
  }
}
