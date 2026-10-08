import { useMutation } from '@tanstack/react-query';
import { generarReporteApi, previewReporteApi } from './apiReportes';
import type {
  ReporteParams,
  ReportePreviewParams,
  ReportePreviewResponse,
} from './types';

export function useGenerarReporte() {
  return useMutation({
    mutationFn: async (params: ReporteParams) => {
      const { blob, filename } = await generarReporteApi(params);
      const url: string = URL.createObjectURL(blob);
      const a: HTMLAnchorElement = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      return filename;
    },
  });
}

export function useObtenerPreviewReporte() {
  return useMutation<ReportePreviewResponse, Error, ReportePreviewParams>({
    mutationFn: async (params: ReportePreviewParams) => previewReporteApi(params),
  });
}
