/**
 * Respuesta de creación/edición/consulta de un registro del catálogo EPS.
 */
export interface AdminEpsFormResponse {
  tid: number;
  nombre: string;
  nit: string | null;
}
