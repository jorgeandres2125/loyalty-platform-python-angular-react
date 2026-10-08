/**
 * Parámetros de consulta para el listado del catálogo Bancos.
 */
export interface AdminBancoListQuery {
  page: number;
  page_size: number;
  nombre?: string;
}
