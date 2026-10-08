import type { AdminEpsListItem } from './AdminEpsListItem';

/**
 * Respuesta paginada del listado del catálogo EPS.
 */
export interface AdminEpsListResponse {
  items: AdminEpsListItem[];
  total: number;
  page: number;
  page_size: number;
}
