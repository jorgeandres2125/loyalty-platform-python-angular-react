import { describe, it, expect } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { useToast } from "./useToast";

describe("useToast", () => {
  it("agrega un toast y luego lo cierra", () => {
    const { result } = renderHook(() => useToast());
    expect(result.current.toasts).toHaveLength(0);

    let id = 0;
    act(() => {
      id = result.current.success("Listo", { title: "Exito" });
    });
    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].bgColor).toBe("success");
    expect(result.current.toasts[0].message).toBe("Listo");

    act(() => {
      result.current.closeToast(id);
    });
    expect(result.current.toasts).toHaveLength(0);
  });

  it("apila multiples toasts con ids unicos", () => {
    const { result } = renderHook(() => useToast());
    act(() => {
      result.current.error("A");
      result.current.info("B");
    });
    expect(result.current.toasts).toHaveLength(2);
    expect(result.current.toasts[0].id).not.toBe(result.current.toasts[1].id);
  });

  it("propaga el mensaje y el detalle del error", () => {
    const { result } = renderHook(() => useToast());
    act(() => {
      result.current.error("No se pudo subir el archivo.", { detail: "413: muy grande" });
    });
    expect(result.current.toasts[0].message).toBe("No se pudo subir el archivo.");
    expect(result.current.toasts[0].detail).toBe("413: muy grande");
  });
});
