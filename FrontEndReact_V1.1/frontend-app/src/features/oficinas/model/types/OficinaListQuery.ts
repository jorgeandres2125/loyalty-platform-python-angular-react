export interface OficinaListQuery {
  page: number;
  page_size: number;
  nombre?: string;
  marca?: string;
  regional?: string;
  ind_activo?: boolean;
}
