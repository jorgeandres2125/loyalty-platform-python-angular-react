/**
 * Parámetros de consulta para el listado del catálogo EPS.
 */
export interface AdminEpsListQuery {
  page: number;
  page_size: number;
  nombre?: string;
}
