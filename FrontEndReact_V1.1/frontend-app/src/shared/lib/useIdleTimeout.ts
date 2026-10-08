import { useEffect, useRef } from 'react';

const EVENTOS_ACTIVIDAD = [
  'mousemove',
  'mousedown',
  'keydown',
  'click',
  'scroll',
  'touchstart',
  'wheel',
] as const;

export interface UseIdleTimeoutOptions {
  idleMs: number;
  warningMs: number;
  active: boolean;
  onWarning: () => void;
  onTimeout: () => void;
  onActivity?: () => void;
  activityThrottleMs?: number;
}

export function useIdleTimeout({
  idleMs,
  warningMs,
  active,
  onWarning,
  onTimeout,
  onActivity,
  activityThrottleMs = 30_000,
}: UseIdleTimeoutOptions): void {
  const onWarningRef = useRef(onWarning);
  onWarningRef.current = onWarning;
  const onTimeoutRef = useRef(onTimeout);
  onTimeoutRef.current = onTimeout;
  const onActivityRef = useRef(onActivity);
  onActivityRef.current = onActivity;
  const ultimaActividadRef = useRef<number>(0);

  useEffect(() => {
    if (!active) return;
    let idWarning: ReturnType<typeof setTimeout>;
    let idTimeout: ReturnType<typeof setTimeout>;
    const canal =
      typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('sufi-sesion') : null;

    const armar = (): void => {
      clearTimeout(idWarning);
      clearTimeout(idTimeout);
      idWarning = setTimeout(() => onWarningRef.current(), Math.max(0, idleMs - warningMs));
      idTimeout = setTimeout(() => onTimeoutRef.current(), idleMs);
    };

    const registrar = (propagar: boolean): void => {
      armar();
      const ahora = Date.now();
      if (onActivityRef.current && ahora - ultimaActividadRef.current >= activityThrottleMs) {
        ultimaActividadRef.current = ahora;
        onActivityRef.current();
      }
      if (propagar && canal) canal.postMessage('actividad');
    };

    const handler = (): void => registrar(true);
    EVENTOS_ACTIVIDAD.forEach((ev) => window.addEventListener(ev, handler, { passive: true }));
    if (canal) {
      canal.onmessage = (e: MessageEvent): void => {
        if (e.data === 'actividad') armar();
        if (e.data === 'logout') onTimeoutRef.current();
      };
    }
    armar();

    return () => {
      clearTimeout(idWarning);
      clearTimeout(idTimeout);
      EVENTOS_ACTIVIDAD.forEach((ev) => window.removeEventListener(ev, handler));
      if (canal) canal.close();
    };
  }, [active, idleMs, warningMs, activityThrottleMs]);
}