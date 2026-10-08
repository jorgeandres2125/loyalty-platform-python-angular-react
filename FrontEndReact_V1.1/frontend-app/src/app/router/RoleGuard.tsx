import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../entities/user/model/authStore';

interface Props {
  roles: string[];
  children: React.ReactNode;
}

export function RoleGuard({ roles, children }: Props) {
  const hasRole = useAuthStore((s) => s.hasRole);

  if (roles.length > 0 && !roles.some((r) => hasRole(r))) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
