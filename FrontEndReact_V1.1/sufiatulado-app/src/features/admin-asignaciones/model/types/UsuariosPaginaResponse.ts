import type { UsuarioCuentaItem } from './UsuarioCuentaItem';

export interface UsuariosPaginaResponse {
  items: UsuarioCuentaItem[];
  total: number;
  page: number;
  page_size: number;
}