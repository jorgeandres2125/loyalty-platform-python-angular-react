import type { ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

/**
 * Crea un wrapper con un `QueryClient` aislado por test y reintentos
 * desactivados, para usar con `renderHook`/`render` al probar hooks de
 * React Query. Sin `retry: false` los tests de error tardarían y harían
 * timeout esperando reintentos.
 */
export function createQueryWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { Wrapper, queryClient };
}
