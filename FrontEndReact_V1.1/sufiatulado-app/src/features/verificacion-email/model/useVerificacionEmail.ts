import { useMutation } from '@tanstack/react-query';
import { confirmarCodigoApi, solicitarCodigoApi } from './apiVerificacionEmail';

// Solicita el envío del código OTP al correo declarado en el perfil (AP-0004).
export function useSolicitarCodigo() {
  return useMutation({ mutationFn: solicitarCodigoApi });
}

// Confirma el código de 8 dígitos recibido por correo.
export function useConfirmarCodigo() {
  return useMutation({ mutationFn: confirmarCodigoApi });
}
