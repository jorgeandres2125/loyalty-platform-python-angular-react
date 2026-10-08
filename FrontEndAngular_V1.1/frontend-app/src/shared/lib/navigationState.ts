import { inject } from '@angular/core';
import { Router } from '@angular/router';

/**
 * Lee el `state` de la navegación actual (equivalente a `useLocation().state` de
 * React Router). Usa la navegación en curso y, si ya terminó, `history.state`.
 * Debe llamarse en un contexto de inyección (p. ej. inicializador de campo).
 */
export function navigationState<T extends object>(): Partial<T> {
  const router = inject(Router);
  const actual = router.getCurrentNavigation()?.extras.state;
  if (actual) return actual as Partial<T>;
  const historico: unknown = typeof history !== 'undefined' ? history.state : null;
  return (historico && typeof historico === 'object' ? historico : {}) as Partial<T>;
}
