import type { EjecutivoFormPayload } from './EjecutivoFormPayload';

export interface EjecutivoFormResponse extends EjecutivoFormPayload {
  id: number;
  perfil_nombre: string;
}
