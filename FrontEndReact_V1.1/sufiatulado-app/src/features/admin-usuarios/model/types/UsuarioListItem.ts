/**
 * Ítem del listado de cuentas de usuario del Panel de Control (AP-0001).
 * `activo` refleja dbo.users.status (1 = puede iniciar sesión, 0 = deshabilitada).
 * Endpoints en /api/v1/admin/usuarios (requiere rol administrator/webmaster).
 */
export interface UsuarioListItem {
  uid: number;
  nombre: string;
  email: string;
  activo: boolean;
  roles: string[];
}
