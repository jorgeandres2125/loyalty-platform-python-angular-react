// AP-0137: validacion de tamano de archivos en el cliente. El limite real lo
// expone el backend en GET /config/uploads; este valor es el respaldo si aun
// no se ha cargado y coincide con el default del backend (10 MB).
export const MAX_UPLOAD_BYTES_FALLBACK = 10_485_760 as const;

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${Math.round(kb)} KB`;
  return `${(kb / 1024).toFixed(2)} MB`;
}

export class ArchivoDemasiadoGrandeError extends Error {
  readonly tamano: number;
  readonly maximo: number;
  constructor(tamano: number, maximo: number) {
    super(
      `El archivo (${formatBytes(tamano)}) supera el tamano maximo permitido de ${formatBytes(maximo)}.`,
    );
    this.name = "ArchivoDemasiadoGrandeError";
    this.tamano = tamano;
    this.maximo = maximo;
  }
}

export function validarTamanoArchivo(file: File, maxBytes: number): void {
  if (file.size > maxBytes) {
    throw new ArchivoDemasiadoGrandeError(file.size, maxBytes);
  }
}
