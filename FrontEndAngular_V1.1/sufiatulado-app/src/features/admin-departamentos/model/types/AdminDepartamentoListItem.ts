/**
 * Ítem del listado del catálogo Departamentos del Panel de Control administrativo.
 * Endpoints en /api/v1/admin/departamentos (requiere rol administrator).
 */
export interface AdminDepartamentoListItem {
  did: number;
  pid: number | null;
  departamento: string;
}
