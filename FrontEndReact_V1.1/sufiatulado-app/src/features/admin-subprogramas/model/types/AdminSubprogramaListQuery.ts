/**
 * Parámetros de consulta para el listado del catálogo Subprogramas.
 */
export interface AdminSubprogramaListQuery {
  page: number;
  page_size: number;
  nombre?: string;
  cpid?: number;
}
