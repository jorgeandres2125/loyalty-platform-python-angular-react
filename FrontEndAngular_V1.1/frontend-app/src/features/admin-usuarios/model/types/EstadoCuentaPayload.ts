/**
 * Cuerpo del cambio de estado de una cuenta (habilitar/deshabilitar).
 * `motivo` es opcional y queda registrado para auditoría futura.
 */
export interface EstadoCuentaPayload {
  activo: boolean;
  motivo?: string | null;
}
