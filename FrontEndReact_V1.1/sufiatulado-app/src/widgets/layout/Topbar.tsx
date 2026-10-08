import { useMemo, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../entities/user/model/authStore';
import { logoutApi } from '../../features/auth/model/apiAuth';
import { ROLES } from '../../shared/config/constants';
import { navigateWithTransition } from '../../shared/lib/viewTransition';
import { limpiarSesionLocal } from '../../shared/lib/limpiarSesionLocal';
import { BrandLogo } from '../../shared/ui/components/BrandLogo';

interface NavItem {
  to: string;
  icon: string;
  label: string;
}

const FALLBACK_ICON = 'bi-grid' as const;

const PANEL_ROLES: ReadonlySet<string> = new Set([
  ROLES.ADMIN,
  ROLES.WEBMASTER,
  ROLES.COMISIONISTA,
  ROLES.COMISIONISTA_CONSUMO,
  ROLES.ASESOR_CONSUMO,
  ROLES.ASESOR_LOGISTICO,
  ROLES.ASESOR_COMERCIAL,
  ROLES.ASESOR_CALLCENTER,
]);

export function Topbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();
  const modulosVisibles = useAuthStore((state) => state.modulosVisibles);

  const navItems: NavItem[] = useMemo(() => {
    const dbItems: NavItem[] = modulosVisibles()
      .filter((modulo) => modulo.ruta && modulo.module_code !== 'PANEL_ADMIN')
      .map((modulo) => ({
        to: modulo.ruta as string,
        icon: modulo.icono ?? FALLBACK_ICON,
        label: modulo.nombre,
      }));

    const tienePanel: boolean =
      user?.roles.some((r) => PANEL_ROLES.has(r)) ?? false;

    if (tienePanel) {
      dbItems.push({
        to: '/admin/dashboard',
        icon: 'bi-grid-3x3-gap-fill',
        label: 'Panel de Control',
      });
    }

    return dbItems;
  }, [modulosVisibles, user]);

  function handleLogout() {
    // Borra la cookie de sesión en el backend (fire-and-forget) y limpia el estado.
    void logoutApi().catch(() => undefined);
    limpiarSesionLocal(queryClient);
    navigateWithTransition(() => navigate('/login'));
  }

  return (
    <header className="topbar">

      {/* ── Main bar ── */}
      <div className="topbar__bar">

        {/* Logo */}
        <NavLink to="/dashboard" className="topbar__logo">
          <BrandLogo height={36} />
        </NavLink>

        {/* Desktop nav — visible from xl up */}
        <nav className="topbar__nav d-none d-xl-flex" aria-label="Navegación principal">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/dashboard'}
              className={({ isActive }) => `topbar__nav-link${isActive ? ' active' : ''}`}
            >
              <i className={`bi ${item.icon}`} aria-hidden="true" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Right side */}
        <div className="topbar__actions">
          {user ? (
            <>
              <span className="topbar__user-email d-none d-xxl-inline">{user.email}</span>
              <button className="topbar__logout-btn" onClick={handleLogout} title="Cerrar sesión">
                <div className="topbar__avatar">{user.username.charAt(0).toUpperCase()}</div>
                <span className="d-none d-sm-inline">{user.username}</span>
                <i className="bi bi-box-arrow-right" />
              </button>
            </>
          ) : (
            <NavLink to="/login" className="topbar__login-link">
              <i className="bi bi-box-arrow-in-right" />
              Ingresar
            </NavLink>
          )}

          {/* Hamburger — visible below xl */}
          <button
            className="topbar__hamburger d-xl-none"
            onClick={() => setMenuOpen((prev) => !prev)}
            aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'}
            aria-expanded={menuOpen}
          >
            <i className={`bi ${menuOpen ? 'bi-x-lg' : 'bi-list'}`} />
          </button>
        </div>
      </div>

      {/* ── Mobile / tablet dropdown ── */}
      {menuOpen && (
        <nav className="topbar__mobile-nav" aria-label="Menú móvil">
          <div className="topbar__mobile-grid">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/dashboard'}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) => `topbar__mobile-link${isActive ? ' active' : ''}`}
              >
                <i className={`bi ${item.icon}`} />
                {item.label}
              </NavLink>
            ))}
          </div>

          {user && (
            <button
              className="topbar__mobile-logout"
              onClick={() => { setMenuOpen(false); handleLogout(); }}
            >
              <i className="bi bi-box-arrow-right" />
              Cerrar sesión
            </button>
          )}
        </nav>
      )}
    </header>
  );
}
