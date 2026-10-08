export interface EjecutivoListQuery {
  page: number;
  page_size: number;
  tipo_doc?: string;
  documento?: string;
  perfil?: string;
  estado?: boolean;
}
