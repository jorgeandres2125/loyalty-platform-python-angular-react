/**
 * Parámetros de consulta para el listado del catálogo AFP.
 */
export interface AdminAfpListQuery {
  page: number;
  page_size: number;
  nombre?: string;
}
