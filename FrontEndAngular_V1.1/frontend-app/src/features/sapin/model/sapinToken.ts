import { Injectable, inject } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../../shared/api/client';
import { QUERY_KEYS } from '../../../shared/config/constants';
import { AuthStore } from '../../../entities/user/model/authStore';
import type { SapinTokenResponse } from './types';

@Injectable({ providedIn: 'root' })
export class SapinApi {
  private readonly api = inject(ApiClient);

  async getToken(): Promise<SapinTokenResponse> {
    const { data } = await this.api.get<SapinTokenResponse>('/sapin/token');
    return data;
  }
}

export function injectSapinToken() {
  const api = inject(SapinApi);
  const auth = inject(AuthStore);
  return injectQuery(() => ({
    queryKey: [QUERY_KEYS.SAPIN_TOKEN],
    queryFn: () => api.getToken(),
    enabled: auth.canAccessSapin(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 4 * 60 * 1000, // refresh every 4 min
  }));
}
