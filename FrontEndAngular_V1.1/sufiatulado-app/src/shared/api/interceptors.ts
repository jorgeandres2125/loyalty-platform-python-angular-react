import { HttpErrorResponse, type HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import {
  CSRF_COOKIE,
  CSRF_HEADER,
  RATE_LIMIT_BURST,
  RATE_LIMIT_ENABLED,
  RATE_LIMIT_REFILL_PER_SEC,
} from '../config/constants';
import { BurstLimiter, RateLimitError } from './burstLimiter';
import { limpiarAlmacenamientoSesion } from '../lib/limpiarSesionLocal';

const METODOS_SEGUROS: ReadonlySet<string> = new Set(['GET', 'HEAD', 'OPTIONS']);

// AP-0206: limitador de rafaga del lado del cliente (token bucket), configurable en
// src/environments. Evita el consumo masivo de los servicios; complementa el rate
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

/**
 * AP-0206: si se excede la rafaga configurada, se aborta la peticion en el
 * navegador (no llega a viajar) para no consumir masivamente los servicios.
 */
export const burstLimitInterceptor: HttpInterceptorFn = (req, next) => {
  if (RATE_LIMIT_ENABLED && !burstLimiter.intentar()) {
    return throwError(() => new RateLimitError());
  }
  return next(req);
};

/**
 * Proteccion CSRF double-submit: en metodos mutadores reenviamos el valor de la
 * cookie CSRF (legible) en la cabecera X-CSRF-Token que el backend valida.
 */
export const csrfInterceptor: HttpInterceptorFn = (req, next) => {
  if (!METODOS_SEGUROS.has(req.method.toUpperCase())) {
    const csrf = leerCookie(CSRF_COOKIE);
    if (csrf) {
      return next(req.clone({ setHeaders: { [CSRF_HEADER]: csrf } }));
    }
  }
  return next(req);
};

/**
 * AP-0132: sesion inexistente o expirada -> descartar los datos locales del
 * navegador y volver a login. La recarga (replace) destruye ademas la memoria.
 */
export const sesionExpiradaInterceptor: HttpInterceptorFn = (req, next) =>
  next(req).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse && error.status === 401) {
        const url: string = req.url ?? '';
        if (!url.includes('/auth/login')) {
          limpiarAlmacenamientoSesion();
          window.location.replace('/login');
        }
      }
      return throwError(() => error);
    }),
  );
