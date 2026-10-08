import { effect, signal, type Signal } from '@angular/core';

/**
 * Devuelve un signal que refleja `source` tras `delay` ms sin cambios
 * (equivalente al hook `useDebounce`). Debe llamarse en un contexto de inyección.
 */
export function debounced<T>(source: Signal<T>, delay: number): Signal<T> {
  const out = signal<T>(source());
  effect((onCleanup) => {
    const value: T = source();
    const timer = setTimeout(() => out.set(value), delay);
    onCleanup(() => clearTimeout(timer));
  });
  return out.asReadonly();
}
