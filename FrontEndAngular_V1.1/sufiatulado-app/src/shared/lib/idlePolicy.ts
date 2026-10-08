const ROLES_CANAL: ReadonlySet<string> = new Set([
  'comisionista',
  'comisionista_consumo',
  'comisionista consumo',
  'ejecutivo',
  'asesor_logistico',
  'asesor_comercial',
  'asesor_callcenter',
]);

export const IDLE_WARNING_MS = 60_000;

/** AP-0129: limite de inactividad en ms segun los roles. Canales 7 min, otras 20 min. */
export function limiteInactividadMs(roles: readonly string[]): number {
  const esCanal = roles.some((rol) => ROLES_CANAL.has(rol));
  return (esCanal ? 7 : 20) * 60_000;
}

export function esCanalPorRoles(roles: readonly string[]): boolean {
  return roles.some((rol) => ROLES_CANAL.has(rol));
}