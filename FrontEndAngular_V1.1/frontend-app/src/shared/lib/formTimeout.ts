import { effect, type Signal } from '@angular/core';

interface FormTimeoutOptions {
  /** Milisegundos hasta el vencimiento. */
  delayMs: number;
  /** El temporizador solo corre cuando es `true` (p. ej. tras la 1ª interacción). */
  active: Signal<boolean>;
  /** Acción al vencer — normalmente, borrar los datos que no se hayan enviado. */
  onTimeout: () => void;
  /**
   * Si se pasa y su valor cambia, el temporizador se reinicia (modo "inactividad").
   * Omitirlo deja un límite ABSOLUTO desde que `active` pasa a `true` (lo que pide
   * AP-0018): el plazo no se reinicia aunque el usuario siga escribiendo.
   */
  resetKey?: Signal<unknown>;
}

/**
 * Temporizador de seguridad para formularios sensibles (AP-0018), equivalente a
 * `useFormTimeout`: vencido el plazo, ejecuta `onTimeout` para borrar los datos de
 * autenticación no enviados. Se cancela al destruir el componente o cuando cambian
 * `active` / `resetKey`. Debe llamarse en un contexto de inyección.
 */
export function formTimeout({ delayMs, active, onTimeout, resetKey }: FormTimeoutOptions): void {
  effect((onCleanup) => {
    resetKey?.();
    if (!active()) return;
    const id = setTimeout(() => onTimeout(), delayMs);
    onCleanup(() => clearTimeout(id));
  });
}
