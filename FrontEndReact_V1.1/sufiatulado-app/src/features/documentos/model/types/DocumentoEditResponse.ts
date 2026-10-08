export interface DocumentoEditResponse {
  did: number;
  numero_documento: string;
  tipo: number;
  tipo_nombre: string;
  nombre: string;
  estado: string;
  version: number;
  fecha: string | null;
}
