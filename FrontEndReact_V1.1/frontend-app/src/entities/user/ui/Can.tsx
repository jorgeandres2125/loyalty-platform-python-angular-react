import type { ReactNode } from 'react';
import { usePermissions } from '../model/usePermissions';
import type { AccionModulo } from '../model/types';

interface CanProps {
  modulo: string;
  accion?: AccionModulo;
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Renderiza children solo si el usuario tiene la accion sobre el modulo.
 * Uso: <Can modulo="REPORTES" accion="exportar"><BotonExportar /></Can>
 */
export function Can({ modulo, accion = 'ver', children, fallback = null }: CanProps) {
  const { can } = usePermissions();
  return <>{can(modulo, accion) ? children : fallback}</>;
}