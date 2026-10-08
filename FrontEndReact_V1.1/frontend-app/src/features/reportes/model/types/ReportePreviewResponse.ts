export interface ReportePreviewResponse {
  columns: string[];
  rows: Array<Array<string | number | boolean | null>>;
  total: number;
  page: number;
  page_size: number;
}
