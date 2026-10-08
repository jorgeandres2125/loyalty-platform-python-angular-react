/**
 * Respuesta de creación/edición/consulta de un registro del catálogo Departamentos.
 */
export interface AdminDepartamentoFormResponse {
  did: number;
  pid: number | null;
  departamento: string;
}
