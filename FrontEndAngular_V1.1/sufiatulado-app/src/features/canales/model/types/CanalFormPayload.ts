export interface CanalFormPayload {
  nom_canales: string;
  cpid: number | null;
  cspid: number | null;
  ind_activo: boolean;
  oficinas_ids: number[];
}
