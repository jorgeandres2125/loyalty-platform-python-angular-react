/**
 * Shape del catálogo MAESTRO de sub-programas (cpid puede ser null si no
 * pertenece a un programa específico).
 */
export interface SubprogramaItem {
  cspid: number;
  cspid_nombre: string;
  cpid: number | null;
}
