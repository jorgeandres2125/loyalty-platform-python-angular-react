/**
 * Helper para `useEffect` ad-hoc que ejecutan trabajo asíncrono.
 *
 * Devuelve un par {run, isCancelled, cleanup}. Úsalo dentro del useEffect cuando
 * NO puedas usar React Query (que ya cancela solo). Si el efecto se desmonta o
 * sus deps cambian, las llamadas a `setState` posteriores se ignoran.
 *
 * @example
 * useEffect(() => {
 *   const { run, isCancelled } = withCancellation();
 *   run(async () => {
 *     const data = await fetchAlgo();
 *     if (isCancelled()) return;
 *     setData(data);
 *   });
 *   return () => withCancellation;  // ← OJO: ver patrón abajo
 * }, [dep]);
 *
 * Patrón canónico recomendado (más explícito que el helper):
 *
 *   useEffect(() => {
 *     let cancelled = false;
 *     (async () => {
 *       const data = await fetchAlgo();
 *       if (cancelled) return;
 *       setData(data);
 *     })();
 *     return () => { cancelled = true; };
 *   }, [dep]);
 *
 * El helper existe sólo para casos donde quieras encapsular el flag.
 */
export interface CancellationToken {
  run: (work: () => Promise<void>) => void;
  isCancelled: () => boolean;
  cancel: () => void;
}

export function withCancellation(): CancellationToken {
  let cancelled: boolean = false;
  return {
    run: (work: () => Promise<void>): void => {
      work().catch((err: unknown) => {
        if (!cancelled) {
          console.error('[withCancellation] uncaught async error:', err);
        }
      });
    },
    isCancelled: (): boolean => cancelled,
    cancel: (): void => {
      cancelled = true;
    },
  };
}
