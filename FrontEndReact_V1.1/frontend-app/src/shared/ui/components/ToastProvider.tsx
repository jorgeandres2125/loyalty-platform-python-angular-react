import type { ReactNode } from "react";
import { ToastStack } from "./CustomToast";
import type { ToastPosition } from "./CustomToast";
import { useToast } from "../hooks/useToast";
import type { UseToastResult } from "../hooks/useToast";
import { ToastContext } from "../hooks/useToastContext";

// Monta el estado de toasts una sola vez y pinta el ToastStack global.
// Cualquier componente accede con useToastContext() (sin prop-drilling).
export function ToastProvider({
  children,
  position = "top-end",
}: {
  children: ReactNode;
  position?: ToastPosition;
}) {
  const toast: UseToastResult = useToast();
  return (
    <ToastContext.Provider value={toast}>
      {children}
      <ToastStack toasts={toast.toasts} onClose={toast.closeToast} position={position} />
    </ToastContext.Provider>
  );
}
