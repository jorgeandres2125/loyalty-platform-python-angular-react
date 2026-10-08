/**
 * Ítem del listado del catálogo Ciudades del Panel de Control administrativo.
 * Endpoints en /api/v1/admin/ciudades (requiere rol administrator).
 */
export interface AdminCiudadListItem {
  cid: number;
  did: number | null;
  ciudad: string;
}
