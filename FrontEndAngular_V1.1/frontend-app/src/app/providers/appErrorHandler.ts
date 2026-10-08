import { ErrorHandler, Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthStore } from '../../entities/user/model/authStore';
import { isApiError } from '../../shared/api/apiError';
import { RateLimitError } from '../../shared/api/burstLimiter';

/**
 * Equivalente al `ErrorBoundary` del proyecto React: ante un error no controlado de la
 * UI se registra y se redirige a una ruta segura ('/' con sesión, '/login' sin ella).
 * Los errores HTTP y de rate limit ya los gestionan las queries/mutaciones, por lo
 * que solo se registran.
 */
@Injectable()
export class AppErrorHandler implements ErrorHandler {
  private readonly router = inject(Router);
  private readonly auth = inject(AuthStore);
  private redirigiendo = false;

  handleError(error: unknown): void {
    console.error(error);
    const causa: unknown = (error as { rejection?: unknown })?.rejection ?? error;
    if (isApiError(causa) || causa instanceof RateLimitError) return;
    if (this.redirigiendo) return;
    this.redirigiendo = true;
    const destino: string = this.auth.isAuthenticated() ? '/' : '/login';
    void this.router.navigateByUrl(destino, { replaceUrl: true }).finally(() => {
      this.redirigiendo = false;
    });
  }
}
