// Tipos del flujo de verificación de propiedad del correo (AP-0004 — doble opt-in).
// Espejo de los esquemas Pydantic del backend (verificacion_email_router).

export interface SolicitarCodigoRequest {
  tipo_documento: string;
  numero_documento: string;
}

export interface SolicitarCodigoResponse {
  enviado: boolean;
  mensaje: string;
  email_enmascarado: string | null;
  expira_en_horas: number | null;
}

export interface ConfirmarCodigoRequest {
  tipo_documento: string;
  numero_documento: string;
  codigo: string;
}

export interface ConfirmarCodigoResponse {
  verificado: boolean;
  mensaje: string;
}
