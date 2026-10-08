import { inject } from '@angular/core';
import { injectMutation } from '@tanstack/angular-query-experimental';
import { ReportesApi } from './apiReportes';
import type { ReporteParams, ReportePreviewParams, ReportePreviewResponse } from './types';

export function injectGenerarReporte() {
  const api = inject(ReportesApi);
  return injectMutation(() => ({
    mutationFn: async (params: ReporteParams): Promise<string> => {
      const { blob, filename } = await api.generar(params);
      const url: string = URL.createObjectURL(blob);
      const a: HTMLAnchorElement = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      return filename;
    },
  }));
}

export function injectObtenerPreviewReporte() {
  const api = inject(ReportesApi);
  return injectMutation<ReportePreviewResponse, Error, ReportePreviewParams>(() => ({
    mutationFn: async (params: ReportePreviewParams) => api.preview(params),
  }));
}
