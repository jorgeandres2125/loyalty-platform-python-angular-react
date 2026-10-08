/**
 * Cuerpo para actualizar los 6 flags de un rol sobre un módulo.
 */
export interface AutorizacionFlagsPayload {
  puede_ver: boolean;
  puede_crear: boolean;
  puede_editar: boolean;
  puede_eliminar: boolean;
  puede_exportar: boolean;
  puede_aprobar: boolean;
}
