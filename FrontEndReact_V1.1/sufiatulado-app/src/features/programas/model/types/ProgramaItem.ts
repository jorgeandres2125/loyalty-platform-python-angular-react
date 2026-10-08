/**
 * Shape del catálogo MAESTRO de programas (entidad no-nullable).
 * No confundir con `ProgramaItem` de `shared/api/catalogos`, que es la
 * referencia opcional embebida en otras entidades.
 */
export interface ProgramaItem {
  cpid: number;
  cp_nombre: string;
}
