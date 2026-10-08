import type { AdminArlListItem } from './AdminArlListItem';

/**
 * Respuesta paginada del listado del catálogo ARL.
 */
export interface AdminArlListResponse {
  items: AdminArlListItem[];
  total: number;
  page: number;
  page_size: number;
}
