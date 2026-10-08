import { useCallback, useState } from "react";
import type { ReactNode } from "react";
import type { ToastStackInstance, ToastVariant } from "../components/CustomToast";

export interface NotifyOptions {
  title?: string;
  message: string;
  detail?: string;
  bgColor?: ToastVariant;
  icon?: ReactNode;
  delay?: number;
}

type AtajoOptions = Omit<NotifyOptions, "message" | "bgColor">;

export interface UseToastResult {
  toasts: ToastStackInstance[];
  notify: (opts: NotifyOptions) => number;
  closeToast: (id: number) => void;
  success: (message: string, opts?: AtajoOptions) => number;
  error: (message: string, opts?: AtajoOptions) => number;
  warning: (message: string, opts?: AtajoOptions) => number;
  info: (message: string, opts?: AtajoOptions) => number;
}

let _contador = 0;
function siguienteId(): number {
  _contador += 1;
  return _contador;
}

// Maneja la logica de mostrar/ocultar toasts desde cualquier componente.
// Pintar junto a <ToastStack toasts={toasts} onClose={closeToast} />.
export function useToast(): UseToastResult {
  const [toasts, setToasts] = useState<ToastStackInstance[]>([]);

  const closeToast = useCallback((id: number): void => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const notify = useCallback((opts: NotifyOptions): number => {
    const id: number = siguienteId();
    setToasts((prev) => [...prev, { id, ...opts }]);
    return id;
  }, []);

  const success = useCallback(
    (message: string, opts?: AtajoOptions): number =>
      notify({ bgColor: "success", message, ...opts }),
    [notify],
  );
  const error = useCallback(
    (message: string, opts?: AtajoOptions): number =>
      notify({ bgColor: "danger", message, ...opts }),
    [notify],
  );
  const warning = useCallback(
    (message: string, opts?: AtajoOptions): number =>
      notify({ bgColor: "warning", message, ...opts }),
    [notify],
  );
  const info = useCallback(
    (message: string, opts?: AtajoOptions): number =>
      notify({ bgColor: "info", message, ...opts }),
    [notify],
  );

  return { toasts, notify, closeToast, success, error, warning, info };
}
