/**
 * Rol del sistema (dbo.role). Sujeto de la parametrización de autorizaciones.
 * Endpoints en /api/v1/admin/autorizaciones (requiere rol administrator).
 */
export interface RolItem {
  rid: number;
  name: string;
}
