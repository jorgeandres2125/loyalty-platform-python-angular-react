import type { ReporteParams } from './ReporteParams';

export interface ReportePreviewParams extends ReporteParams {
  page: number;
  page_size: number;
}
