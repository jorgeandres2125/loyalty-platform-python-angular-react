import { Injectable, inject } from '@angular/core';
import { injectMutation } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../../shared/api/client';
import type {
  ConfirmarCodigoRequest,
  ConfirmarCodigoResponse,
  SolicitarCodigoRequest,
  SolicitarCodigoResponse,
} from './typesVerificacionEmail';

// Endpoints PÚBLICOS (sin JWT): el código enviado al correo es lo que prueba la
// identidad del titular. Ver AP-0004 (backend verificacion_email_router).
@Injectable({ providedIn: 'root' })
export class VerificacionEmailApi {
  private readonly api = inject(ApiClient);

  async solicitarCodigo(payload: SolicitarCodigoRequest): Promise<SolicitarCodigoResponse> {
    const response = await this.api.post<SolicitarCodigoResponse>('/verificacion-email/solicitar', payload);
    return response.data;
  }

  async confirmarCodigo(payload: ConfirmarCodigoRequest): Promise<ConfirmarCodigoResponse> {
    const response = await this.api.post<ConfirmarCodigoResponse>('/verificacion-email/confirmar', payload);
    return response.data;
  }
}

// Solicita el envío del código OTP al correo declarado en el perfil (AP-0004).
export function injectSolicitarCodigo() {
  const api = inject(VerificacionEmailApi);
  return injectMutation(() => ({
    mutationFn: (payload: SolicitarCodigoRequest) => api.solicitarCodigo(payload),
  }));
}

// Confirma el código de 8 dígitos recibido por correo.
export function injectConfirmarCodigo() {
  const api = inject(VerificacionEmailApi);
  return injectMutation(() => ({
    mutationFn: (payload: ConfirmarCodigoRequest) => api.confirmarCodigo(payload),
  }));
}
