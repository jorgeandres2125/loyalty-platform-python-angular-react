/**
 * Ítem del listado del catálogo ARL del Panel de Control administrativo.
 * Endpoints en /api/v1/admin/arl (requiere rol administrator).
 */
export interface AdminArlListItem {
  tid: number;
  nombre: string;
  nit: string | null;
}
