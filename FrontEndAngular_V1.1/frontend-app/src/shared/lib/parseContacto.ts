/**
 * Helpers puros para parsear el contacto/perfil recibido del backend, que puede
 * llegar como objeto anidado ({codigo}, {nombre}, {did}, ...) o como escalar.
 *
 * AP-0036: centralizan el narrowing de tipos para que los efectos de carga de los
 * formularios no acumulen complejidad ciclomática.
 */

export function strDe(v: unknown): string {
  return v === null || v === undefined ? '' : String(v);
}

export function refObj(raw: unknown): Record<string, unknown> | null {
  return typeof raw === 'object' && raw !== null ? (raw as Record<string, unknown>) : null;
}

export function refId(raw: unknown, key: string): number | '' {
  if (typeof raw === 'object' && raw !== null) {
    const v = (raw as Record<string, unknown>)[key];
    return typeof v === 'number' ? v : '';
  }
  return typeof raw === 'number' ? raw : '';
}

export function parseTipoDoc(raw: unknown): string {
  if (typeof raw === 'object' && raw !== null) {
    return (raw as Record<string, string>).codigo ?? 'CC';
  }
  return typeof raw === 'string' ? raw : 'CC';
}

export function parseGenero(raw: unknown, mapa: Record<string, string>): string {
  if (typeof raw === 'object' && raw !== null) {
    return (raw as Record<string, string>).nombre ?? '';
  }
  if (typeof raw === 'string') {
    return mapa[raw] ?? raw;
  }
  return '';
}

export function parseEstado(v: unknown): 0 | 1 | null {
  if (v === 1) return 1;
  if (v === 0) return 0;
  return null;
}

export function parseBoolOrNull(v: unknown): boolean | null {
  return v !== undefined && v !== null ? Boolean(v) : null;
}

export function parseNumOrNull(v: unknown): number | null {
  return v !== undefined && v !== null ? Number(v) : null;
}

export function fechaCorta(v: unknown): string {
  return typeof v === 'string' ? v.slice(0, 10) : '';
}
