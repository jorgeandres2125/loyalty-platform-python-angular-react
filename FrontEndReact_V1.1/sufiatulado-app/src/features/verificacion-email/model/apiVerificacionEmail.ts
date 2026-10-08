import { apiClient } from '../../../shared/api/client';
import type {
  ConfirmarCodigoRequest,
  ConfirmarCodigoResponse,
  SolicitarCodigoRequest,
  SolicitarCodigoResponse,
} from './typesVerificacionEmail';

// Endpoints PÚBLICOS (sin JWT): el código enviado al correo es lo que prueba la
// identidad del titular. Ver AP-0004 (backend verificacion_email_router).

export async function solicitarCodigoApi(
  payload: SolicitarCodigoRequest,
): Promise<SolicitarCodigoResponse> {
  const response = await apiClient.post<SolicitarCodigoResponse>(
    '/verificacion-email/solicitar',
    payload,
  );
  return response.data;
}

export async function confirmarCodigoApi(
  payload: ConfirmarCodigoRequest,
): Promise<ConfirmarCodigoResponse> {
  const response = await apiClient.post<ConfirmarCodigoResponse>(
    '/verificacion-email/confirmar',
    payload,
  );
  return response.data;
}
