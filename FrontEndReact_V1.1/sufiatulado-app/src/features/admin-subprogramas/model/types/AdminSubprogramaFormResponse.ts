/**
 * Respuesta de creación/edición/consulta de un registro del catálogo Subprogramas.
 */
export interface AdminSubprogramaFormResponse {
  cspid: number;
  cspid_nombre: string;
  cpid: number | null;
}
