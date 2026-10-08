/**
 * Ítem del listado del catálogo Subprogramas del Panel de Control administrativo.
 * Endpoints en /api/v1/admin/subprogramas (requiere rol administrator).
 */
export interface AdminSubprogramaListItem {
  cspid: number;
  cspid_nombre: string;
  cpid: number | null;
}
