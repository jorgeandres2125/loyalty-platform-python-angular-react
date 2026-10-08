import { effect, untracked, type Signal } from '@angular/core';

const EVENTOS_ACTIVIDAD = [
  'mousemove',
  'mousedown',
  'keydown',
  'click',
  'scroll',
  'touchstart',
  'wheel',
] as const;

export interface IdleTimeoutOptions {
  idleMs: Signal<number>;
  warningMs: number;
  active: Signal<boolean>;
  onWarning: () => void;
  onTimeout: () => void;
  onActivity?: () => void;
  activityThrottleMs?: number;
}

/**
 * AP-0129: detección de inactividad (equivalente a `useIdleTimeout`). Arma un aviso
 * `warningMs` antes del vencimiento y cierra al cumplirse `idleMs`. La actividad se
 * propaga entre pestañas con BroadcastChannel ('sufi-sesion'). Debe llamarse en un
 * contexto de inyección; se desmonta solo al destruir el componente.
 */
export function idleTimeout({
  idleMs,
  warningMs,
  active,
  onWarning,
  onTimeout,
  onActivity,
  activityThrottleMs = 30_000,
}: IdleTimeoutOptions): void {
  let ultimaActividad = 0;

  effect((onCleanup) => {
    if (!active()) return;
    const limiteMs: number = idleMs();

    untracked(() => {
      let idWarning: ReturnType<typeof setTimeout> | undefined;
      let idTimeout: ReturnType<typeof setTimeout> | undefined;
      const canal: BroadcastChannel | null =
        typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('sufi-sesion') : null;

      const armar = (): void => {
        clearTimeout(idWarning);
        clearTimeout(idTimeout);
        idWarning = setTimeout(() => onWarning(), Math.max(0, limiteMs - warningMs));
        idTimeout = setTimeout(() => onTimeout(), limiteMs);
      };

      const registrar = (propagar: boolean): void => {
        armar();
        const ahora: number = Date.now();
        if (onActivity && ahora - ultimaActividad >= activityThrottleMs) {
          ultimaActividad = ahora;
          onActivity();
        }
        if (propagar && canal) canal.postMessage('actividad');
      };

      const handler = (): void => registrar(true);
      EVENTOS_ACTIVIDAD.forEach((ev) => window.addEventListener(ev, handler, { passive: true }));
      if (canal) {
        canal.onmessage = (e: MessageEvent): void => {
          if (e.data === 'actividad') armar();
          if (e.data === 'logout') onTimeout();
        };
      }
      armar();

      onCleanup(() => {
        clearTimeout(idWarning);
        clearTimeout(idTimeout);
        EVENTOS_ACTIVIDAD.forEach((ev) => window.removeEventListener(ev, handler));
        if (canal) canal.close();
      });
    });
  });
}
