import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useMiDetalleMovilidad } from './useMiPerfilMovilidad';

// Regresion: PerfilMovilidadPage tiene efectos con dependencia [detalle.data] que hacen
// setState. Si `data` fuese un objeto literal nuevo en cada render, esos efectos se
// dispararian siempre -> setState -> re-render -> bucle infinito ("Maximum update depth
// exceeded"). El hook debe devolver identidades ESTABLES entre renders.

vi.mock('../../../shared/api/client', () => ({
  apiClient: {
    get: vi.fn((url: string) => {
      if (url === '/me/perfil-contacto') return Promise.resolve({ data: { contacto: { celular: '3001234567' } } });
      if (url === '/me/perfil-tributario') return Promise.resolve({ data: { tributario: { eps: 1 } } });
      if (url === '/me/perfil-emocional') return Promise.resolve({ data: { emocional: { hobbies: 'x' } } });
      return Promise.resolve({ data: {} });
    }),
  },
}));

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useMiDetalleMovilidad', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('agrega contacto, tributario y emocional desde los endpoints /me/*', async () => {
    const { result } = renderHook(() => useMiDetalleMovilidad(), { wrapper });
    await waitFor(() => expect(result.current.data).toBeDefined());
    expect(result.current.data).toEqual({
      contacto: { celular: '3001234567' },
      tributario: { eps: 1 },
      emocional: { hobbies: 'x' },
    });
  });

  it('mantiene la identidad de data estable entre renders (evita bucle infinito)', async () => {
    const { result, rerender } = renderHook(() => useMiDetalleMovilidad(), { wrapper });
    await waitFor(() => expect(result.current.data).toBeDefined());

    const primera = result.current.data;
    rerender();
    rerender();

    // Misma referencia: los efectos [detalle.data] de la pagina no se re-disparan.
    expect(result.current.data).toBe(primera);
  });

  it('mantiene la identidad de refetch estable entre renders', async () => {
    const { result, rerender } = renderHook(() => useMiDetalleMovilidad(), { wrapper });
    await waitFor(() => expect(result.current.data).toBeDefined());

    const primera = result.current.refetch;
    rerender();

    expect(result.current.refetch).toBe(primera);
  });
});
