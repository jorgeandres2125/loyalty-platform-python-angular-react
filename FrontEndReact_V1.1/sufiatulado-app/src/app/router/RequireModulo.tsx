import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { usePermissions } from '../../entities/user/model/usePermissions';
import type { AccionModulo } from '../../entities/user/model/types';

interface RequireModuloProps {
  modulo: string;
  accion?: AccionModulo;
  redirectTo?: string;
}

/**
 * Guard de ruta por modulo + accion. Anidar bajo ProtectedRoute (que ya valida
 * sesion). Si falta sesion -> /login; si falta el permiso -> redirectTo.
 */
export function RequireModulo({ modulo, accion = 'ver', redirectTo = '/dashboard' }: RequireModuloProps) {
  const { isAuthenticated, can } = usePermissions();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (!can(modulo, accion)) {
    return <Navigate to={redirectTo} replace />;
  }
  return <Outlet />;
}