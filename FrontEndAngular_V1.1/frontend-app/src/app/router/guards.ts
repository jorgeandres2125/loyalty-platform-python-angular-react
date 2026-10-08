import { inject } from '@angular/core';
import { RedirectCommand, Router, type CanActivateFn, type CanMatchFn } from '@angular/router';
import { AuthStore } from '../../entities/user/model/authStore';
import type { AccionModulo } from '../../entities/user/model/types';

/** Rutas protegidas: sin sesion -> /login (equivalente a `ProtectedRoute`). */
export const protectedGuard: CanActivateFn = (_route, state) => {
  const auth = inject(AuthStore);
  const router = inject(Router);
  if (!auth.isAuthenticated()) {
    return new RedirectCommand(router.parseUrl('/login'), {
      replaceUrl: true,
      state: { from: state.url },
    });
  }
  return true;
};

/** Rutas publicas (login): con sesion -> /dashboard (equivalente a `PublicRoute`). */
export const publicGuard: CanActivateFn = () => {
  const auth = inject(AuthStore);
  const router = inject(Router);
  return auth.isAuthenticated() ? router.createUrlTree(['/dashboard']) : true;
};

/**
 * Guard de ruta por modulo + accion (equivalente a `RequireModulo`). Anidar bajo
 * `protectedGuard` (que ya valida sesion). Si falta sesion -> /login; si falta el
 * permiso -> redirectTo.
 */
export function requireModulo(
  modulo: string,
  accion: AccionModulo = 'ver',
  redirectTo: string = '/dashboard',
): CanActivateFn {
  return () => {
    const auth = inject(AuthStore);
    const router = inject(Router);
    if (!auth.isAuthenticated()) {
      return router.createUrlTree(['/login']);
    }
    if (!auth.puedeAcceder(modulo, accion)) {
      return router.createUrlTree([redirectTo]);
    }
    return true;
  };
}

/** Gating por rol (equivalente a `RoleGuard`). */
export function roleGuard(roles: string[]): CanMatchFn {
  return () => {
    const auth = inject(AuthStore);
    const router = inject(Router);
    if (roles.length > 0 && !roles.some((r) => auth.hasRole(r))) {
      return router.createUrlTree(['/dashboard']);
    }
    return true;
  };
}
