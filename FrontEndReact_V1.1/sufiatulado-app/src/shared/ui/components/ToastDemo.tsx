import { useState } from "react";
import Button from "react-bootstrap/Button";
import { CustomToast, ToastStack } from "./CustomToast";
import { useToast } from "../hooks/useToast";

// Ejemplo de uso (equivalente al App.jsx solicitado).
export function ToastDemo() {
  const [show, setShow] = useState<boolean>(false);
  const { toasts, success, error, info, closeToast } = useToast();

  return (
    <div className="p-4 d-flex gap-2 flex-wrap">
      <Button variant="primary" onClick={() => setShow(true)}>
        Toast simple
      </Button>
      <Button
        variant="success"
        onClick={() => success("Operacion realizada con exito.", { title: "Exito", icon: "OK" })}
      >
        Exito (hook)
      </Button>
      <Button
        variant="danger"
        onClick={() => error("No se pudo completar la accion.", { title: "Error" })}
      >
        Error (hook)
      </Button>
      <Button variant="info" onClick={() => info("Tienes una nueva notificacion.")}>
        Info (hook)
      </Button>

      <CustomToast
        show={show}
        onClose={() => setShow(false)}
        title="Notificacion"
        message="Este es un toast reusable con Bootstrap."
        bgColor="success"
        icon="OK"
        delay={10000}
        position="top-end"
      />

      <ToastStack toasts={toasts} onClose={closeToast} position="bottom-end" />
    </div>
  );
}
