import type { ReporteTipo } from './ReporteTipo';

export interface ReporteParams {
  tipo: ReporteTipo;
  programa?: number;
  subprograma?: number | null;
  fecha_inicio?: string;
  fecha_fin?: string;
  cedula?: string;
  estado?: number;
}
