export interface CanalFormResponse {
  cod_canales: number;
  nom_canales: string;
  cpid: number | null;
  cspid: number | null;
  ind_activo: boolean;
  id_canales: number;
  oficinas_ids: number[];
}
