import { isApiError } from '../../../shared/api/apiError';

export interface GraciaExpiradaInfo {
  username?: string;
  diasRestantesGracia?: number;
}

// AP-0038: detecta la respuesta 409 de contrasena vencida en gracia y extrae los datos
// para redirigir al cambio autonomo por vencimiento. Devuelve null para cualquier otro
// error (401, 403 fuera de gracia, error de red), que el formulario muestra normalmente.
export function graciaExpiradaDeError(error: unknown): GraciaExpiradaInfo | null {
  if (!isApiError(error) || error.response?.status !== 409) {
    return null;
  }
  const data = error.response?.data as {
    code?: string;
    username?: string;
    dias_restantes_gracia?: number;
  };
  if (data?.code !== 'password_expired_in_grace') {
    return null;
  }
  return { username: data.username, diasRestantesGracia: data.dias_restantes_gracia };
}
