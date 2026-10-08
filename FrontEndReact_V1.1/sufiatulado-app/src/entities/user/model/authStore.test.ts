import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from './authStore';
import { TOKEN_KEY } from '../../../shared/config/constants';
import { makeAuthUser, makeModulo } from '../../../test/fixtures';

// El store es un singleton con `persist`; lo reseteamos antes de cada prueba.
// (El `localStorage.clear()` vive en src/test/setup.ts → afterEach.)
beforeEach(() => {
  useAuthStore.setState({ user: null, sapinToken: null });
});

describe('authStore — setAuth / logout', () => {
  it('setAuth guarda el usuario en el estado y NO escribe el token en localStorage', () => {
    const user = makeAuthUser();
    useAuthStore.getState().setAuth(user);

    expect(useAuthStore.getState().user).toEqual(user);
    // Medida A: el token de sesión nunca se almacena en el cliente (vive en cookie HttpOnly).
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
  });

  it('logout limpia el estado (incluido sapinToken) y borra la clave sufi-auth de localStorage', () => {
    useAuthStore.getState().setAuth(makeAuthUser());
    useAuthStore.getState().setSapinToken('sapin-xyz');

    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.sapinToken).toBeNull();
    // clearStorage() debe eliminar la clave por completo, no dejar { user: null }
    expect(localStorage.getItem('sufi-auth')).toBeNull();
  });
});

describe('authStore — hasRole', () => {
  it('devuelve true para un rol que el usuario posee', () => {
    useAuthStore.setState({ user: makeAuthUser({ roles: ['ejecutivo_consumo'] }) });
    expect(useAuthStore.getState().hasRole('ejecutivo_consumo')).toBe(true);
  });

  it('devuelve false para un rol ausente y cuando no hay usuario', () => {
    useAuthStore.setState({ user: makeAuthUser({ roles: ['comisionista'] }) });
    expect(useAuthStore.getState().hasRole('administrator')).toBe(false);

    useAuthStore.setState({ user: null });
    expect(useAuthStore.getState().hasRole('comisionista')).toBe(false);
  });
});

describe('authStore — puedeAcceder', () => {
  it('el administrator puede todo sin importar los flags del módulo', () => {
    useAuthStore.setState({ user: makeAuthUser({ roles: ['administrator'], modulos: [] }) });
    expect(useAuthStore.getState().puedeAcceder('CUALQUIERA', 'eliminar')).toBe(true);
  });

  it('respeta el flag por acción del módulo correspondiente', () => {
    const modulo = makeModulo({
      module_code: 'CANALES',
      puede_ver: true,
      puede_editar: true,
      puede_eliminar: false,
    });
    useAuthStore.setState({ user: makeAuthUser({ roles: ['webmaster'], modulos: [modulo] }) });

    const store = useAuthStore.getState();
    expect(store.puedeAcceder('CANALES')).toBe(true); // 'ver' por defecto
    expect(store.puedeAcceder('CANALES', 'editar')).toBe(true);
    expect(store.puedeAcceder('CANALES', 'eliminar')).toBe(false);
  });

  it('devuelve false si el módulo no existe o no hay usuario', () => {
    useAuthStore.setState({ user: makeAuthUser({ roles: ['webmaster'], modulos: [] }) });
    expect(useAuthStore.getState().puedeAcceder('NO_EXISTE')).toBe(false);

    useAuthStore.setState({ user: null });
    expect(useAuthStore.getState().puedeAcceder('CANALES')).toBe(false);
  });
});

describe('authStore — modulosVisibles', () => {
  it('filtra los no visibles y ordena por `orden` ascendente', () => {
    const user = makeAuthUser({
      modulos: [
        makeModulo({ module_code: 'C', orden: 3, puede_ver: true }),
        makeModulo({ module_code: 'A', orden: 1, puede_ver: true }),
        makeModulo({ module_code: 'OCULTO', orden: 2, puede_ver: false }),
      ],
    });
    useAuthStore.setState({ user });

    const visibles = useAuthStore.getState().modulosVisibles();
    expect(visibles.map((m) => m.module_code)).toEqual(['A', 'C']);
  });

  it('devuelve [] cuando no hay usuario', () => {
    useAuthStore.setState({ user: null });
    expect(useAuthStore.getState().modulosVisibles()).toEqual([]);
  });
});

describe('authStore — canAccessSapin', () => {
  it('true para comisionista CON incentivos', () => {
    useAuthStore.setState({
      user: makeAuthUser({ roles: ['comisionista'], tiene_incentivos: true }),
    });
    expect(useAuthStore.getState().canAccessSapin()).toBe(true);
  });

  it('true para comisionista_consumo CON incentivos', () => {
    useAuthStore.setState({
      user: makeAuthUser({ roles: ['comisionista_consumo'], tiene_incentivos: true }),
    });
    expect(useAuthStore.getState().canAccessSapin()).toBe(true);
  });

  it('false para comisionista SIN incentivos', () => {
    useAuthStore.setState({
      user: makeAuthUser({ roles: ['comisionista'], tiene_incentivos: false }),
    });
    expect(useAuthStore.getState().canAccessSapin()).toBe(false);
  });

  it('false para un rol no elegible aunque tenga incentivos', () => {
    useAuthStore.setState({
      user: makeAuthUser({ roles: ['ejecutivo_consumo'], tiene_incentivos: true }),
    });
    expect(useAuthStore.getState().canAccessSapin()).toBe(false);
  });

  it('false cuando no hay usuario', () => {
    useAuthStore.setState({ user: null });
    expect(useAuthStore.getState().canAccessSapin()).toBe(false);
  });
});

describe('authStore — isAuthenticated', () => {
  // La sesión real la respalda la cookie HttpOnly del backend; el cliente solo
  // refleja si hay un `user` cargado (un 401 lo limpia y redirige a /login).
  it('true cuando hay un usuario cargado', () => {
    useAuthStore.setState({ user: makeAuthUser() });
    expect(useAuthStore.getState().isAuthenticated()).toBe(true);
  });

  it('false cuando no hay usuario', () => {
    useAuthStore.setState({ user: null });
    expect(useAuthStore.getState().isAuthenticated()).toBe(false);
  });
});
