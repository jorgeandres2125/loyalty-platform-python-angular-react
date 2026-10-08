/**
 * Parámetros de consulta para el listado del catálogo ARL.
 */
export interface AdminArlListQuery {
  page: number;
  page_size: number;
  nombre?: string;
}
