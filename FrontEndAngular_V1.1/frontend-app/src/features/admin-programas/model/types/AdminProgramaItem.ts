/**
 * Ítem del catálogo Programas del Panel de Control administrativo.
 * Endpoints en /api/v1/admin/programas (requiere rol administrator).
 */
export interface AdminProgramaItem {
  cpid: number;
  cp_nombre: string;
}
