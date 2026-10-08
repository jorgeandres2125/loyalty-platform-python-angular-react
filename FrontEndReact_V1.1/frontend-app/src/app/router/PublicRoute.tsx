import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../../entities/user/model/authStore';

export function PublicRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated());

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
