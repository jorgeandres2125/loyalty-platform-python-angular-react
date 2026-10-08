import axios from 'axios';

export interface TemporalRequeridaInfo {
  username?: string;
  expiraIso?: string;
}

// AP-0046: detecta la respuesta 409 de contrasena temporal (requiere cambio
// obligatorio) y extrae los datos para redirigir a la pagina dedicada. Devuelve
// null para cualquier otro error, que el formulario de login muestra normalmente.
export function temporalRequeridaDeError(error: unknown): TemporalRequeridaInfo | null {
  if (!axios.isAxiosError(error) || error.response?.status !== 409) {
    return null;
  }
  const data = error.response.data as {
    code?: string;
    username?: string;
    expira_iso?: string;
  };
  if (data?.code !== 'password_temporal_change_required') {
    return null;
  }
  return { username: data.username, expiraIso: data.expira_iso };
}
