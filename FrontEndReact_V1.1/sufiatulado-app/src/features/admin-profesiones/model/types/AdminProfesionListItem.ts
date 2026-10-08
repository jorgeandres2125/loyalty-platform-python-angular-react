/**
 * Ítem del listado del catálogo Profesiones del Panel de Control administrativo.
 * Endpoints en /api/v1/admin/profesiones (requiere rol administrator).
 */
export interface AdminProfesionListItem {
  tid: number;
  nombre: string;
}
