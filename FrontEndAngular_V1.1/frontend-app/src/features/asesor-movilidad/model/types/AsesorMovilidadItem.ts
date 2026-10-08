import type {
  TipoDocumentoItem,
  GeneroItem,
  DepartamentoItem,
  CiudadItem,
  ProgramaItem,
} from '../../../../shared/api/catalogos';

export interface AsesorMovilidadItem {
  numero_documento: string;
  nombre_completo: string | null;
  tipo_documento: TipoDocumentoItem | null;
  genero: GeneroItem | null;
  celular: string | null;
  programa: ProgramaItem | null;
  departamento: DepartamentoItem | null;
  ciudad: CiudadItem | null;
  estado: number | null;
  fecha_completado: string | null;
  incentivos: boolean | null;
}
