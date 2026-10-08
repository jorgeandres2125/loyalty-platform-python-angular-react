import type { AdminSubprogramaListItem } from './AdminSubprogramaListItem';

/**
 * Respuesta paginada del listado del catálogo Subprogramas.
 */
export interface AdminSubprogramaListResponse {
  items: AdminSubprogramaListItem[];
  total: number;
  page: number;
  page_size: number;
}
