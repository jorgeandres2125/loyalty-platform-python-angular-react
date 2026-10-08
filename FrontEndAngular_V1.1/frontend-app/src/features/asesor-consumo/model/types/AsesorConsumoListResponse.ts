import type { AsesorConsumoItem } from './AsesorConsumoItem';

export interface AsesorConsumoListResponse {
  items: AsesorConsumoItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
