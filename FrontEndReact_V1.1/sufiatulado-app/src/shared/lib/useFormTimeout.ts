import { useEffect, useRef } from 'react';

interface UseFormTimeoutOptions {
  /** Milisegundos hasta el vencimiento. */
  delayMs: number;
  /** El temporizador solo corre cuando es `true` (p. ej. tras la 1ª interacción). */
  active: boolean;
  /** Acción al vencer — normalmente, borrar los datos que no se hayan enviado. */
  onTimeout: () => void;
  /**
   * Si se pasa y su valor cambia, el temporizador se reinicia (modo "inactividad").
   * Omitirlo deja un límite ABSOLUTO desde que `active` pasa a `true` (lo que pide
   * AP-0018): el plazo no se reinicia aunque el usuario siga escribiendo.
   */
  resetKey?: unknown;
}

/**
 * Temporizador de seguridad para formularios sensibles (AP-0018): vencido el plazo,
 * ejecuta `onTimeout` para borrar los datos de autenticación no enviados. Cancela el
 * `setTimeout` al desmontar o cuando cambian las dependencias, evitando fugas.
 *
 * `onTimeout` se guarda en una `ref` para no recrear el temporizador en cada render;
 * así el plazo absoluto se mantiene estable mientras `active`/`resetKey` no cambien.
 */
export function useFormTimeout({
  delayMs,
  active,
  onTimeout,
  resetKey,
}: UseFormTimeoutOptions): void {
  const onTimeoutRef = useRef<() => void>(onTimeout);
  onTimeoutRef.current = onTimeout;

  useEffect(() => {
    if (!active) return;
    const id = setTimeout(() => onTimeoutRef.current(), delayMs);
    return () => clearTimeout(id);
  }, [active, delayMs, resetKey]);
}
