import type { ReactNode } from "react";
import Toast from "react-bootstrap/Toast";
import ToastContainer from "react-bootstrap/ToastContainer";

export type ToastVariant =
  | "success"
  | "danger"
  | "warning"
  | "info"
  | "primary"
  | "secondary"
  | "dark"
  | "light";

export type ToastPosition =
  | "top-start"
  | "top-center"
  | "top-end"
  | "middle-start"
  | "middle-center"
  | "middle-end"
  | "bottom-start"
  | "bottom-center"
  | "bottom-end";

// Variantes de fondo oscuro: el texto y el boton de cierre van en claro.
const VARIANTES_OSCURAS: ReadonlySet<ToastVariant> = new Set([
  "success",
  "danger",
  "primary",
  "secondary",
  "dark",
  "info",
]);

// Error y advertencia se anuncian de forma asertiva a lectores de pantalla;
// el resto, de forma cortes (polite). Accesibilidad basica (a11y).
function ariaLive(variant: ToastVariant): "assertive" | "polite" {
  return variant === "danger" || variant === "warning" ? "assertive" : "polite";
}

export interface ToastVisualProps {
  title?: string;
  message?: string;
  detail?: string;
  bgColor?: ToastVariant;
  icon?: ReactNode;
  delay?: number;
  autohide?: boolean;
}

interface ToastItemProps extends ToastVisualProps {
  show: boolean;
  onClose: () => void;
}

// Toast individual (sin contenedor). Reutilizado por CustomToast y ToastStack.
export function ToastItem({
  show,
  onClose,
  title = "Notificacion",
  message = "",
  detail,
  bgColor = "primary",
  icon,
  delay = 10000,
  autohide = true,
}: ToastItemProps) {
  const oscuro: boolean = VARIANTES_OSCURAS.has(bgColor);
  return (
    <Toast
      show={show}
      onClose={onClose}
      delay={delay}
      autohide={autohide}
      bg={bgColor}
      role="alert"
      aria-live={ariaLive(bgColor)}
      aria-atomic="true"
    >
      <Toast.Header closeButton closeVariant={oscuro ? "white" : undefined}>
        {icon != null ? (
          <span className="me-2 fs-5 lh-1" aria-hidden="true">
            {icon}
          </span>
        ) : null}
        <strong className="me-auto">{title}</strong>
      </Toast.Header>
      {message || detail ? (
        <Toast.Body className={oscuro ? "text-white" : undefined}>
          {message ? <div>{message}</div> : null}
          {detail ? <div className="small mt-1 opacity-75">{detail}</div> : null}
        </Toast.Body>
      ) : null}
    </Toast>
  );
}

export interface CustomToastProps extends ToastVisualProps {
  show: boolean;
  onClose: () => void;
  position?: ToastPosition;
}

// Toast autocontenido (incluye su ToastContainer). Para un unico toast
// controlado por estado (show / onClose).
export function CustomToast({ position = "top-end", ...props }: CustomToastProps) {
  return (
    <ToastContainer position={position} className="p-3" style={{ zIndex: 1090 }}>
      <ToastItem {...props} />
    </ToastContainer>
  );
}

export interface ToastStackInstance extends ToastVisualProps {
  id: number;
}

interface ToastStackProps {
  toasts: ReadonlyArray<ToastStackInstance>;
  onClose: (id: number) => void;
  position?: ToastPosition;
}

// Bonus: apila multiples toasts en un unico contenedor (stacking).
export function ToastStack({ toasts, onClose, position = "top-end" }: ToastStackProps) {
  return (
    <ToastContainer position={position} className="p-3" style={{ zIndex: 1090 }}>
      {toasts.map(({ id, ...rest }) => (
        <ToastItem key={id} show onClose={() => onClose(id)} {...rest} />
      ))}
    </ToastContainer>
  );
}
