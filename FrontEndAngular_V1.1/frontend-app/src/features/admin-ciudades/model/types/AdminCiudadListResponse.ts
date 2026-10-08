import type { AdminCiudadListItem } from './AdminCiudadListItem';

/**
 * Respuesta paginada del listado del catálogo Ciudades.
 */
export interface AdminCiudadListResponse {
  items: AdminCiudadListItem[];
  total: number;
  page: number;
  page_size: number;
}
