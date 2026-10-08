import type {
  TipoDocumentoItem,
  GeneroItem,
  DepartamentoItem,
  CiudadItem,
  ProgramaItem,
} from '../../../../shared/api/catalogos';
import type { CanalesItem } from './CanalesItem';
import type { OficinaItem } from './OficinaItem';
import type { SubprogramaItem } from './SubprogramaItem';

export interface AsesorConsumoItem {
  numero_documento: string;
  nombre_completo: string | null;
  tipo_documento: TipoDocumentoItem | null;
  genero: GeneroItem | null;
  celular: string | null;
  canal: CanalesItem | null;
  oficina: OficinaItem | null;
  programa: ProgramaItem | null;
  subprograma: SubprogramaItem | null;
  departamento: DepartamentoItem | null;
  ciudad: CiudadItem | null;
  estado: number | null;
  fecha_completado: string | null;
  incentivos: boolean | null;
}
