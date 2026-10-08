import { Injectable, computed, inject, type Signal } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../../shared/api/client';
import { MAX_UPLOAD_BYTES_FALLBACK } from '../../../shared/lib/archivos';

export interface UploadLimits {
  max_upload_bytes: number;
  max_upload_mb: number;
}

@Injectable({ providedIn: 'root' })
export class ConfigApi {
  private readonly api = inject(ApiClient);

  async getUploadLimits(): Promise<UploadLimits> {
    const { data } = await this.api.get<UploadLimits>('/config/uploads');
    return data;
  }
}

// AP-0137: limite de subida que publica el backend; cacheado 1 hora.
export function injectUploadLimits() {
  const api = inject(ConfigApi);
  return injectQuery(() => ({
    queryKey: ['config', 'upload-limits'],
    queryFn: () => api.getUploadLimits(),
    staleTime: 3_600_000,
  }));
}

// Devuelve el limite vigente en bytes: el del backend si cargo, o el respaldo.
export function injectMaxUploadBytes(): Signal<number> {
  const limits = injectUploadLimits();
  return computed<number>(() => limits.data()?.max_upload_bytes ?? MAX_UPLOAD_BYTES_FALLBACK);
}
