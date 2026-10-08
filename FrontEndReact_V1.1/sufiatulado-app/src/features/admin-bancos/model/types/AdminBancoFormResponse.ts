/**
 * Respuesta de creación/edición/consulta de un registro del catálogo Bancos.
 */
export interface AdminBancoFormResponse {
  tid: number;
  nombre: string;
  codigo: string | null;
}
