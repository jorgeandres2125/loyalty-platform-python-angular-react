import { strDe } from '../../shared/lib/parseContacto';

/** Campos del perfil emocional (comunes a asesores y perfiles propios). */
export interface FormEmocional {
  con_quien_vives: string;
  estado_civil: string;
  numero_hijos: string;
  info_hijos: string;
  hobbies: string;
  nivel_educativo: string;
  profesion: string;
  temas_a_profundizar: string;
  premios_gustaria_recibir: string;
  propositos_familiares: string;
  propositos_financieros: string;
  propositos_diversion: string;
  propositos_salud: string;
  propositos_competencias: string;
  numero_mascotas: string;
  info_mascotas: string;
  acepto_terminos_y_condiciones: boolean;
}

export const INIT_EMOCIONAL: FormEmocional = {
  con_quien_vives: '',
  estado_civil: '',
  numero_hijos: '',
  info_hijos: '',
  hobbies: '',
  nivel_educativo: '',
  profesion: '',
  temas_a_profundizar: '',
  premios_gustaria_recibir: '',
  propositos_familiares: '',
  propositos_financieros: '',
  propositos_diversion: '',
  propositos_salud: '',
  propositos_competencias: '',
  numero_mascotas: '',
  info_mascotas: '',
  acepto_terminos_y_condiciones: false,
};

export function countSelections(raw: string): number {
  if (!raw) return 0;
  try {
    const parsed: unknown = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed.length;
  } catch {
    return raw.split(',').filter((s) => s.trim()).length;
  }
  return 0;
}

export function badgeCount(s: string): number | null {
  return countSelections(s) || null;
}

/** Mapea el perfil emocional crudo del backend al formulario. */
export function mapearEmocional(e: Record<string, unknown>): FormEmocional {
  return {
    con_quien_vives: strDe(e['con_quien_vives']),
    estado_civil: strDe(e['estado_civil']),
    numero_hijos: strDe(e['numero_hijos']),
    info_hijos: strDe(e['info_hijos']),
    hobbies: strDe(e['hobbies']),
    nivel_educativo: strDe(e['nivel_educativo']),
    profesion: strDe(e['profesion']),
    temas_a_profundizar: strDe(e['temas_a_profundizar']),
    premios_gustaria_recibir: strDe(e['premios_gustaria_recibir']),
    propositos_familiares: strDe(e['propositos_familiares']),
    propositos_financieros: strDe(e['propositos_financieros']),
    propositos_diversion: strDe(e['propositos_diversion']),
    propositos_salud: strDe(e['propositos_salud']),
    propositos_competencias: strDe(e['propositos_competencias']),
    numero_mascotas: strDe(e['numero_mascotas']),
    info_mascotas: strDe(e['info_mascotas']),
    acepto_terminos_y_condiciones: Boolean(e['acepto_terminos_y_condiciones']),
  };
}

/** Payload común del perfil emocional (campos vacíos → null). */
export function payloadEmocional(
  e: FormEmocional,
  numero_documento: string | null,
  comisionista_programa_id: number,
): Record<string, unknown> {
  return {
    numero_documento,
    con_quien_vives: e.con_quien_vives || null,
    estado_civil: e.estado_civil || null,
    numero_hijos: e.numero_hijos || null,
    info_hijos: e.info_hijos || null,
    hobbies: e.hobbies || null,
    nivel_educativo: e.nivel_educativo || null,
    profesion: e.profesion || null,
    temas_a_profundizar: e.temas_a_profundizar || null,
    premios_gustaria_recibir: e.premios_gustaria_recibir || null,
    propositos_familiares: e.propositos_familiares || null,
    propositos_financieros: e.propositos_financieros || null,
    propositos_diversion: e.propositos_diversion || null,
    propositos_salud: e.propositos_salud || null,
    propositos_competencias: e.propositos_competencias || null,
    numero_mascotas: e.numero_mascotas || null,
    info_mascotas: e.info_mascotas || null,
    comisionista_programa_id,
    acepto_terminos_y_condiciones: 1 as const,
  };
}
