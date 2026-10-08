import { describe, it, expect, vi, afterEach } from 'vitest';
import { navigateWithTransition } from './viewTransition';

describe('navigateWithTransition', () => {
  afterEach(() => {
    // Quita cualquier stub de startViewTransition que haya añadido un test.
    delete (document as unknown as { startViewTransition?: unknown }).startViewTransition;
    vi.restoreAllMocks();
  });

  it('usa startViewTransition cuando la API existe', () => {
    const navigateFn = vi.fn();
    const startViewTransition = vi.fn((cb: () => void) => cb());
    (document as unknown as { startViewTransition: unknown }).startViewTransition =
      startViewTransition;

    navigateWithTransition(navigateFn);

    expect(startViewTransition).toHaveBeenCalledTimes(1);
    expect(navigateFn).toHaveBeenCalledTimes(1);
  });

  it('hace fallback a la navegación directa cuando la API no existe', () => {
    // jsdom no implementa startViewTransition, así que esta es la rama por defecto.
    const navigateFn = vi.fn();

    navigateWithTransition(navigateFn);

    expect(navigateFn).toHaveBeenCalledTimes(1);
  });
});
