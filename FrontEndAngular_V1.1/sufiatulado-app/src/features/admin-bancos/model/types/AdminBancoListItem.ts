/**
 * Ítem del listado del catálogo Bancos del Panel de Control administrativo.
 * Endpoints en /api/v1/admin/bancos (requiere rol administrator).
 */
export interface AdminBancoListItem {
  tid: number;
  nombre: string;
  codigo: string | null;
}
