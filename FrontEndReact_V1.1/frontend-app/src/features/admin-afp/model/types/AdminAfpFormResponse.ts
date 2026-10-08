/**
 * Respuesta de creación/edición/consulta de un registro del catálogo AFP.
 */
export interface AdminAfpFormResponse {
  tid: number;
  nombre: string;
  nit: string | null;
}
