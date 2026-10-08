import {
  type ApplicationConfig,
  ErrorHandler,
  LOCALE_ID,
  provideBrowserGlobalErrorListeners,
  provideZonelessChangeDetection,
} from '@angular/core';
import { registerLocaleData } from '@angular/common';
import localeEsCo from '@angular/common/locales/es-CO';
import { provideHttpClient, withInterceptors, withNoXsrfProtection } from '@angular/common/http';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { QueryClient, provideTanStackQuery } from '@tanstack/angular-query-experimental';

import { routes } from './app.routes';
import { AppErrorHandler } from './providers/appErrorHandler';
import {
  burstLimitInterceptor,
  csrfInterceptor,
  sesionExpiradaInterceptor,
} from '../shared/api/interceptors';

registerLocaleData(localeEsCo);

// Misma configuración por defecto que el QueryProvider del proyecto React.
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 0,
      gcTime: 0,
      refetchOnMount: 'always',
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZonelessChangeDetection(),
    provideRouter(routes, withComponentInputBinding()),
    // La protección CSRF double-submit la aplica `csrfInterceptor` (cookie sufi_csrf).
    provideHttpClient(
      withNoXsrfProtection(),
      withInterceptors([burstLimitInterceptor, csrfInterceptor, sesionExpiradaInterceptor]),
    ),
    provideTanStackQuery(queryClient),
    { provide: ErrorHandler, useClass: AppErrorHandler },
    { provide: LOCALE_ID, useValue: 'es-CO' },
  ],
};
