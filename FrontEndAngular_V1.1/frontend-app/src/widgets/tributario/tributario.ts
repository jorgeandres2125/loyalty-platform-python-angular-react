import { computed, effect, untracked, type Signal, type WritableSignal } from '@angular/core';
import { parseBoolOrNull, parseNumOrNull } from '../../shared/lib/parseContacto';

// Identificadores de las opciones "NO COMISION" de los catálogos EPS / AFP / ARL.
export const NO_COMISION_EPS = 7848;
export const NO_COMISION_AFP = 7846;
export const NO_COMISION_ARL = 7847;

export interface FormTributario {
  eps: number | null;
  afp: number | null;
  arl: number | null;
  contratacion_personal: boolean | null;
  regimen_iva: boolean | null;
}

export const INIT_TRIBUTARIO: FormTributario = {
  eps: null,
  afp: null,
  arl: null,
  contratacion_personal: null,
  regimen_iva: null,
};

/** Campos del contacto que se editan junto con la información tributaria. */
export interface DatosComision {
  numero_documento: string;
  requiere_comision: boolean | null;
  banco: number | null;
  tipo_de_cuenta: string;
  numero_de_cuenta: string;
  numero_de_cuenta_verifica: string;
}

export interface DocTributario {
  did: number;
  tipo: number;
  nombre: string;
  version: number;
}

export function boolToBit(b: boolean | null): 0 | 1 | null {
  if (b === null) return null;
  return b ? 1 : 0;
}

export function parseTipoCuenta(v: unknown): string {
  const s = String(v ?? '');
  if (s === '0' || s.toLowerCase().includes('ahor')) return 'Cuenta de ahorros';
  if (s === '1' || s.toLowerCase().includes('corr')) return 'Cuenta corriente';
  return '';
}

export function mapearTributario(t: Record<string, unknown>): FormTributario {
  return {
    eps: parseNumOrNull(t['eps']),
    afp: parseNumOrNull(t['afp']),
    arl: parseNumOrNull(t['arl']),
    contratacion_personal: parseBoolOrNull(t['contratacion_personal']),
    regimen_iva: parseBoolOrNull(t['regimen_iva']),
  };
}

export function payloadTributario(t: FormTributario, numero_documento: string | null): Record<string, unknown> {
  return {
    numero_documento,
    eps: t.eps,
    afp: t.afp,
    arl: t.arl,
    contratacion_personal: boolToBit(t.contratacion_personal),
    regimen_iva: boolToBit(t.regimen_iva),
  };
}

export function validarTributario(c: DatosComision, t: FormTributario): string | null {
  if (c.requiere_comision === null) return 'Debe indicar si el asesor trabaja Con Comisión o Sin Comisión';
  if (c.requiere_comision === true) {
    if (t.eps === null || t.eps === NO_COMISION_EPS) return 'Con Comisión: debe seleccionar una EPS distinta a NO COMISION';
    if (t.afp === null || t.afp === NO_COMISION_AFP)
      return 'Con Comisión: debe seleccionar un Fondo de Pensiones distinto a NO COMISION';
    if (t.arl === null || t.arl === NO_COMISION_ARL) return 'Con Comisión: debe seleccionar una ARL distinta a NO COMISION';
  }
  if (c.numero_de_cuenta && c.numero_de_cuenta !== c.numero_de_cuenta_verifica) {
    return 'Los números de cuenta no coinciden';
  }
  return null;
}

export function docPorTipo<T extends { tipo: number }>(docs: T[] | undefined, tipo: number): T | null {
  return docs?.find((d) => d.tipo === tipo) ?? null;
}

/** Documentos de EPS/AFP/ARL que deben eliminarse porque la entidad quedó en NO COMISION. */
export function documentosTributariosAEliminar(
  t: FormTributario,
  docs: DocTributario[] | undefined,
): number[] {
  const ids: number[] = [];
  const docEps = docPorTipo(docs, 7);
  const docAfp = docPorTipo(docs, 8);
  const docArl = docPorTipo(docs, 9);
  if (t.eps === NO_COMISION_EPS && docEps) ids.push(docEps.did);
  if (t.afp === NO_COMISION_AFP && docAfp) ids.push(docAfp.did);
  if (t.arl === NO_COMISION_ARL && docArl) ids.push(docArl.did);
  return ids;
}

/**
 * Sin/Con Comisión: al pasar a "Sin Comisión" se fuerzan EPS/AFP/ARL a NO COMISION y al
 * volver a "Con Comisión" se restaura el último valor real elegido (no NO COMISION).
 * Equivalente a los efectos `savedEps/savedAfp/savedArl` del proyecto React.
 * Debe llamarse en un contexto de inyección.
 */
export function sincronizarComision(
  contacto: Signal<{ requiere_comision: boolean | null }>,
  tributario: WritableSignal<FormTributario>,
): void {
  const guardados: { eps: number | null; afp: number | null; arl: number | null } = {
    eps: null,
    afp: null,
    arl: null,
  };

  const recordar = (t: FormTributario): void => {
    if (t.eps !== null && t.eps !== NO_COMISION_EPS) guardados.eps = t.eps;
    if (t.afp !== null && t.afp !== NO_COMISION_AFP) guardados.afp = t.afp;
    if (t.arl !== null && t.arl !== NO_COMISION_ARL) guardados.arl = t.arl;
  };

  // Mantiene el último valor "real" de cada entidad.
  effect(() => recordar(tributario()));

  const requiereComision = computed<boolean | null>(() => contacto().requiere_comision);
  effect(() => {
    const requiere = requiereComision();
    untracked(() => {
      recordar(tributario());
      if (requiere === false) {
        tributario.update((prev) => ({
          ...prev,
          eps: NO_COMISION_EPS,
          afp: NO_COMISION_AFP,
          arl: NO_COMISION_ARL,
        }));
      } else if (requiere === true) {
        tributario.update((prev) => ({ ...prev, eps: guardados.eps, afp: guardados.afp, arl: guardados.arl }));
      }
    });
  });
}
