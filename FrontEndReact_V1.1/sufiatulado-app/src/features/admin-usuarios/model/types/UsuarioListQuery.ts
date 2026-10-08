/**
 * Parámetros de consulta para el listado de cuentas de usuario.
 * `activo` filtra por estado de la cuenta (undefined = todas).
 */
export interface UsuarioListQuery {
  page: number;
  page_size: number;
  texto?: string;
  activo?: boolean;
}
