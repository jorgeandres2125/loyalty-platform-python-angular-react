import type { OficinaListItem } from './OficinaListItem';

export interface OficinaListResponse {
  items: OficinaListItem[];
  total: number;
  page: number;
  page_size: number;
}
