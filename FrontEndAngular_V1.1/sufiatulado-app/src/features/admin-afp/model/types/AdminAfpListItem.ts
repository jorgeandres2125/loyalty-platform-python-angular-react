/**
 * Ítem del listado del catálogo AFP del Panel de Control administrativo.
 * Endpoints en /api/v1/admin/afp (requiere rol administrator).
 */
export interface AdminAfpListItem {
  tid: number;
  nombre: string;
  nit: string | null;
}
