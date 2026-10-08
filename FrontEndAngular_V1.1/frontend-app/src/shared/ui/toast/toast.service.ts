import { Injectable, signal } from '@angular/core';

export type ToastVariant =
  | 'success'
  | 'danger'
  | 'warning'
  | 'info'
  | 'primary'
  | 'secondary'
  | 'dark'
  | 'light';

export type ToastPosition =
  | 'top-start'
  | 'top-center'
  | 'top-end'
  | 'middle-start'
  | 'middle-center'
  | 'middle-end'
  | 'bottom-start'
  | 'bottom-center'
  | 'bottom-end';

export interface ToastVisualProps {
  title?: string;
  message?: string;
  detail?: string;
  bgColor?: ToastVariant;
  /** Texto o clase de icono (`bi-…`) que se pinta antes del título. */
  icon?: string;
  delay?: number;
  autohide?: boolean;
}

export interface ToastStackInstance extends ToastVisualProps {
  id: number;
}

export interface NotifyOptions {
  title?: string;
  message: string;
  detail?: string;
  bgColor?: ToastVariant;
  icon?: string;
  delay?: number;
}

type AtajoOptions = Omit<NotifyOptions, 'message' | 'bgColor'>;

let contador = 0;
function siguienteId(): number {
  contador += 1;
  return contador;
}

/**
 * Estado global de toasts (equivalente a `useToast` + `ToastProvider`/`useToastContext`).
 * La lista vive en un signal; `<app-toast-stack>` (montado en el root) la pinta.
 */
@Injectable({ providedIn: 'root' })
export class ToastService {
  private readonly _toasts = signal<ToastStackInstance[]>([]);
  readonly toasts = this._toasts.asReadonly();

  closeToast(id: number): void {
    this._toasts.update((prev) => prev.filter((t) => t.id !== id));
  }

  notify(opts: NotifyOptions): number {
    const id: number = siguienteId();
    this._toasts.update((prev) => [...prev, { id, ...opts }]);
    return id;
  }

  success(message: string, opts?: AtajoOptions): number {
    return this.notify({ bgColor: 'success', message, ...opts });
  }

  error(message: string, opts?: AtajoOptions): number {
    return this.notify({ bgColor: 'danger', message, ...opts });
  }

  warning(message: string, opts?: AtajoOptions): number {
    return this.notify({ bgColor: 'warning', message, ...opts });
  }

  info(message: string, opts?: AtajoOptions): number {
    return this.notify({ bgColor: 'info', message, ...opts });
  }
}
