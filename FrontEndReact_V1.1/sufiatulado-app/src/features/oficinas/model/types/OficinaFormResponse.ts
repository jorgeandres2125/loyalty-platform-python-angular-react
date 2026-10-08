export interface OficinaFormResponse {
  cod_oficinas: number;
  id_oficinas: number | null;
  nom_oficinas: string;
  marca: string;
  regional: string;
  cpid: number | null;
  ind_activo: boolean;
  ciudad_nombre: string;
  did: number | null;
  departamento_nombre: string;
  canales_ids: number[];
}
