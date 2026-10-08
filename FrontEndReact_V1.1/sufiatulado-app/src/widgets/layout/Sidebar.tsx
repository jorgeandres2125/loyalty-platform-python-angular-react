import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../entities/user/model/authStore';
import { usePermissions } from '../../entities/user/model/usePermissions';
import { logoutApi } from '../../features/auth/model/apiAuth';
import { ROLES } from '../../shared/config/constants';
import { navigateWithTransition } from '../../shared/lib/viewTransition';
import { BrandLogo } from '../../shared/ui/components/BrandLogo';

interface NavItem {
  to: string;
  icon: string;
  label: string;
  roles: string[];
}

// Rutas heredadas que aun no tienen module_code en el backend; se muestran por rol.
const EXTRA_ITEMS: NavItem[] = [
  { to: '/documentos', icon: 'bi-file-earmark-text', label: 'Documentos', roles: [ROLES.ADMIN, ROLES.WEBMASTER, ROLES.DOCUMENTADOR] },
  { to: '/referencias', icon: 'bi-diagram-3', label: 'Referencias', roles: [ROLES.ADMIN, ROLES.WEBMASTER] },
];

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: Props) {
  const navigate = useNavigate();
  const { user, logout, hasRole, canAccessSapin } = useAuthStore();
  const { modulos } = usePermissions();

  // Menu data-driven: el backend resuelve roles + permisos en `modulos` (puede_ver
  // ya viene filtrado y ordenado por `orden`). SAPIN conserva su compuerta de
  // incentivos (puede_ver por si solo no la modela).
  const dynamicItems: NavItem[] = modulos
    .filter((m) => m.ruta !== null && m.ruta !== '')
    .filter((m) => (m.module_code === 'SAPIN' ? canAccessSapin() : true))
    .map((m) => ({ to: m.ruta as string, icon: m.icono ?? 'bi-dot', label: m.nombre, roles: [] }));

  const rutasDinamicas: Set<string> = new Set(dynamicItems.map((item) => item.to));
  const extraItems: NavItem[] = EXTRA_ITEMS.filter(
    (item) => !rutasDinamicas.has(item.to) && item.roles.some((rol) => hasRole(rol)),
  );
  const items: NavItem[] = [...dynamicItems, ...extraItems];

  function handleLogout() {
    void logoutApi().catch(() => undefined);
    logout();
    navigateWithTransition(() => navigate('/login'));
  }

  return (
    <>
      {isOpen && (
        <div
          className="d-lg-none position-fixed top-0 start-0 w-100 h-100"
          style={{ background: 'rgba(0,0,0,0.4)', zIndex: 999 }}
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      <aside className={`sidebar ${isOpen ? 'open' : ''}`} aria-label="Navegacion principal">
        <div className="sidebar__logo">
          <BrandLogo height={34} />
        </div>

        <nav className="sidebar__nav">
          <ul className="list-unstyled mb-0">
            {items.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  className={({ isActive }) => `nav-item-link${isActive ? ' active' : ''}`}
                  onClick={onClose}
                  end={item.to === '/dashboard'}
                >
                  <i className={`bi ${item.icon} nav-icon`} aria-hidden="true" />
                  <span>{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="sidebar__footer">
          {user && (
            <div className="mb-3">
              <div className="d-flex align-items-center gap-2">
                <div
                  className="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
                  style={{ width: 32, height: 32, background: 'rgba(255,255,255,0.1)', color: '#fff', fontSize: '0.875rem', fontWeight: 600 }}
                >
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <div className="overflow-hidden">
                  <div className="text-white fw-semibold text-truncate" style={{ fontSize: '0.8rem' }}>
                    {user.username}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)' }}>
                    {user.roles[0] ?? 'usuario'}
                  </div>
                </div>
              </div>
            </div>
          )}
          <button
            className="btn btn-sm w-100 text-start d-flex align-items-center gap-2"
            style={{ color: 'rgba(255,255,255,0.6)', background: 'transparent', border: 'none' }}
            onClick={handleLogout}
          >
            <i className="bi bi-box-arrow-left" />
            Cerrar sesion
          </button>
        </div>
      </aside>
    </>
  );
}