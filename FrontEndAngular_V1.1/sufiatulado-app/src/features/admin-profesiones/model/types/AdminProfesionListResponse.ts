import type { AdminProfesionListItem } from './AdminProfesionListItem';

/**
 * Respuesta paginada del listado del catálogo Profesiones.
 */
export interface AdminProfesionListResponse {
  items: AdminProfesionListItem[];
  total: number;
  page: number;
  page_size: number;
}
