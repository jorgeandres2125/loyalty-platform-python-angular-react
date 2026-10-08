/**
 * Sub-programa con campos NO nullables (id, nombre y FK al programa).
 * Distinto de `SubprogramaItem` (que vive en asesor-consumo y permite nulls).
 */
export interface Subprograma {
  cspid: number;
  cspid_nombre: string;
  cpid: number;
}
