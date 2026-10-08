import type { AdminBancoListItem } from './AdminBancoListItem';

/**
 * Respuesta paginada del listado del catálogo Bancos.
 */
export interface AdminBancoListResponse {
  items: AdminBancoListItem[];
  total: number;
  page: number;
  page_size: number;
}
