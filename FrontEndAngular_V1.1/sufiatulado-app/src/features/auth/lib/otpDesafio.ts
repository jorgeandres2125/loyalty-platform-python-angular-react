import type { OtpDesafio } from '../../../entities/user/model/types';

// AP-0012: la respuesta 202 del login para roles criticos trae un desafio OTP
// en lugar de un token. Detecta esa forma y la normaliza; null si no aplica.
export function otpDesafioDeData(data: unknown): OtpDesafio | null {
  if (typeof data !== 'object' || data === null) {
    return null;
  }
  const obj = data as {
    otp_requerido?: unknown;
    desafio_id?: unknown;
    email_enmascarado?: unknown;
    expira_en_segundos?: unknown;
    mensaje?: unknown;
  };
  if (obj.otp_requerido !== true || typeof obj.desafio_id !== 'string') {
    return null;
  }
  return {
    desafioId: obj.desafio_id,
    emailEnmascarado:
      typeof obj.email_enmascarado === 'string' ? obj.email_enmascarado : '',
    expiraEnSegundos:
      typeof obj.expira_en_segundos === 'number' ? obj.expira_en_segundos : 0,
    mensaje:
      typeof obj.mensaje === 'string'
        ? obj.mensaje
        : 'Ingresa el codigo de acceso que enviamos a tu correo.',
  };
}
