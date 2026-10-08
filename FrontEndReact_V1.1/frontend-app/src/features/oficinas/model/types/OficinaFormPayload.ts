export interface OficinaFormPayload {
  nom_oficinas: string;
  marca: string;
  regional: string;
  cpid: number | null;
  ind_activo: boolean;
  canales_ids: number[];
}
