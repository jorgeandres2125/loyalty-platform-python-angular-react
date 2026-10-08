/**
 * Parámetros de consulta para el listado del catálogo Profesiones.
 */
export interface AdminProfesionListQuery {
  page: number;
  page_size: number;
  nombre?: string;
}
