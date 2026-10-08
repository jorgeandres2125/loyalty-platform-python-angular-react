/**
 * DTOs de catálogos compartidos entre features.
 * Cualquier endpoint que devuelva uno de estos shapes debe importar desde aquí —
 * no duplicar la interfaz en su propio apiXxx.ts.
 *
 * Si el backend cambia el shape de un catálogo, este archivo es el único punto a tocar.
 */

export type { TipoDocumentoItem } from './TipoDocumentoItem';
export type { GeneroItem } from './GeneroItem';
export type { DepartamentoItem } from './DepartamentoItem';
export type { CiudadItem } from './CiudadItem';
export type { ProgramaItem } from './ProgramaItem';
export type { Subprograma } from './Subprograma';
