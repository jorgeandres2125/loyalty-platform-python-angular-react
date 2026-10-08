/**
 * Parámetros de consulta para el listado del catálogo Departamentos.
 */
export interface AdminDepartamentoListQuery {
  page: number;
  page_size: number;
  nombre?: string;
}
