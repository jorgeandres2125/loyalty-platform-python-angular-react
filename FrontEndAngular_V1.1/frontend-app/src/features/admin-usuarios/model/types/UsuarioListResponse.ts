import type { UsuarioListItem } from './UsuarioListItem';

/**
 * Respuesta paginada del listado de cuentas de usuario.
 */
export interface UsuarioListResponse {
  items: UsuarioListItem[];
  total: number;
  page: number;
  page_size: number;
}
