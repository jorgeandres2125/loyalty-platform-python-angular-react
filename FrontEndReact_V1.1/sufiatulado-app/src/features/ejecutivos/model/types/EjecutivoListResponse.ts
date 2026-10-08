import type { EjecutivoListItem } from './EjecutivoListItem';

export interface EjecutivoListResponse {
  items: EjecutivoListItem[];
  total: number;
  page: number;
  page_size: number;
}
