import type { AsesorMovilidadItem } from './AsesorMovilidadItem';

export interface AsesorMovilidadListResponse {
  items: AsesorMovilidadItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
