/**
 * Parámetros de consulta para el listado del catálogo Ciudades.
 */
export interface AdminCiudadListQuery {
  page: number;
  page_size: number;
  nombre?: string;
  did?: number;
}
