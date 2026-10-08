/**
 * Códigos de tipo de reporte aceptados por el backend.
 * Const + type derivado conviven en el mismo archivo porque están acoplados
 * (enum-as-object pattern: el type es derivado del const con `keyof typeof`).
 */
export const REPORTE_TIPO = {
  HOJA_VIDA: 0,
  INFO_LABORAL: 1,
  PLANTILLA_PARTICIPANTES: 2,
  INFO_TRIBUTARIA: 3,
  USUARIOS_MIGRADOS: 4,
  DEFAULT: 5,
  ESTADOS_PERFILES: 6,
} as const;

export type ReporteTipo = (typeof REPORTE_TIPO)[keyof typeof REPORTE_TIPO];
