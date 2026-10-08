/**
 * Respuesta de creación/edición/consulta de un registro del catálogo Ciudades.
 */
export interface AdminCiudadFormResponse {
  cid: number;
  did: number | null;
  ciudad: string;
}
