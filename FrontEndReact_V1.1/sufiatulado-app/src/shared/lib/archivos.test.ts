import { describe, it, expect } from "vitest";
import {
  ArchivoDemasiadoGrandeError,
  MAX_UPLOAD_BYTES_FALLBACK,
  formatBytes,
  validarTamanoArchivo,
} from "./archivos";

function fakeFile(size: number): File {
  return { size } as File;
}

describe("validarTamanoArchivo", () => {
  it("acepta un archivo dentro del limite", () => {
    expect(() => validarTamanoArchivo(fakeFile(100), 1024)).not.toThrow();
  });

  it("rechaza un archivo que excede el limite", () => {
    expect(() => validarTamanoArchivo(fakeFile(2048), 1024)).toThrow(
      ArchivoDemasiadoGrandeError,
    );
  });

  it("el respaldo coincide con 10 MB", () => {
    expect(MAX_UPLOAD_BYTES_FALLBACK).toBe(10_485_760);
  });

  it("formatBytes formatea MB con dos decimales", () => {
    expect(formatBytes(10_485_760)).toBe("10.00 MB");
  });
});
