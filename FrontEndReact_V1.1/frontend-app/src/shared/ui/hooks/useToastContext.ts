import { createContext, useContext } from "react";
import type { UseToastResult } from "./useToast";

// Contexto de toasts compartido entre el ToastProvider y los consumidores.
export const ToastContext = createContext<UseToastResult | null>(null);

// Hook de acceso al contexto. Lanza si se usa fuera del ToastProvider.
export function useToastContext(): UseToastResult {
  const ctx = useContext(ToastContext);
  if (ctx === null) {
    throw new Error("useToastContext debe usarse dentro de <ToastProvider>.");
  }
  return ctx;
}
