import type { AdminDepartamentoListItem } from './AdminDepartamentoListItem';

/**
 * Respuesta paginada del listado del catálogo Departamentos.
 */
export interface AdminDepartamentoListResponse {
  items: AdminDepartamentoListItem[];
  total: number;
  page: number;
  page_size: number;
}
