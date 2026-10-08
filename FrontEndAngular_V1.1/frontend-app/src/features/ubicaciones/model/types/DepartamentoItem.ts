/**
 * Departamento expuesto por `/ubicaciones/departamentos`.
 * Shape distinto al de `shared/api/catalogos.DepartamentoItem` (que incluye `pid`
 * porque representa una referencia opcional embebida en otra entidad).
 */
export interface DepartamentoItem {
  did: number;
  departamento: string;
}
