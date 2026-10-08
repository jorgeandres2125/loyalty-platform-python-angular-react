import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import {
  API_BASE_URL,
  CSRF_COOKIE,
  CSRF_HEADER,
  RATE_LIMIT_ENABLED,
  RATE_LIMIT_BURST,
  RATE_LIMIT_REFILL_PER_SEC,
} from '../config/constants';
import { BurstLimiter, RateLimitError } from './burstLimiter';
import { limpiarAlmacenamientoSesion } from '../lib/limpiarSesionLocal';

const METODOS_SEGUROS = new Set(['GET', 'HEAD', 'OPTIONS']);

// AP-0206: limitador de rafaga del lado del cliente (token bucket), configurable por
// el .env del frontend. Evita el consumo masivo de los servicios; complementa el rate
// limiting del backend (slowapi, AP-0166).
const burstLimiter = new BurstLimiter({
  capacity: RATE_LIMIT_BURST,
  refillPerSec: RATE_LIMIT_REFILL_PER_SEC,
});

function leerCookie(nombre: string): string | null {
  const patron = new RegExp('(?:^|; )' + nombre + '=([^;]*)');
  const match = document.cookie.match(patron);
  return match ? decodeURIComponent(match[1]) : null;
}

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
  // Medida A: la autenticacion viaja en la cookie HttpOnly de sesion, que el
  // navegador adjunta automaticamente cuando withCredentials esta activo.
  withCredentials: true,
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // AP-0206: si se excede la rafaga configurada, se aborta la peticion en el
  // navegador (no llega a viajar) para no consumir masivamente los servicios.
  if (RATE_LIMIT_ENABLED && !burstLimiter.intentar()) {
    throw new RateLimitError();
  }
  // Proteccion CSRF double-submit: en metodos mutadores reenviamos el valor de la
  // cookie CSRF (legible) en la cabecera X-CSRF-Token que el backend valida.
  const metodo = (config.method ?? 'get').toUpperCase();
  if (!METODOS_SEGUROS.has(metodo)) {
    const csrf = leerCookie(CSRF_COOKIE);
    if (csrf) {
      config.headers.set(CSRF_HEADER, csrf);
    }
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      // AP-0132: sesion inexistente o expirada -> descartar los datos locales del
      // navegador y volver a login. La recarga (replace) destruye ademas la memoria.
      const url = error.config?.url ?? '';
      if (!url.includes('/auth/login')) {
        limpiarAlmacenamientoSesion();
        window.location.replace('/login');
      }
    }
    return Promise.reject(error);
  },
);

export { apiClient };
