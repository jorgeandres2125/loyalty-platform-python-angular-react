/**
 * Ítem del listado del catálogo EPS del Panel de Control administrativo.
 * Endpoints en /api/v1/admin/eps (requiere rol administrator).
 */
export interface AdminEpsListItem {
  tid: number;
  nombre: string;
  nit: string | null;
}
