/**
 * Respuesta de creación/edición/consulta de un registro del catálogo ARL.
 */
export interface AdminArlFormResponse {
  tid: number;
  nombre: string;
  nit: string | null;
}
