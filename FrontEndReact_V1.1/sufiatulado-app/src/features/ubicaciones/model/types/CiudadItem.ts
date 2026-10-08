/**
 * Ciudad expuesta por `/ubicaciones/ciudades/{did}`.
 * `did` no-nullable (siempre pertenece a un departamento).
 */
export interface CiudadItem {
  cid: number;
  ciudad: string;
  did: number;
}
