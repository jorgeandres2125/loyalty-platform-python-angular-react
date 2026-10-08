import type { AdminAfpListItem } from './AdminAfpListItem';

/**
 * Respuesta paginada del listado del catálogo AFP.
 */
export interface AdminAfpListResponse {
  items: AdminAfpListItem[];
  total: number;
  page: number;
  page_size: number;
}
