import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { createQueryWrapper } from '../../../test/queryWrapper';

vi.mock('./apiSesiones', () => ({
  listarMisSesionesApi: vi.fn(),
  cerrarSesionApi: vi.fn(),
  cerrarOtrasSesionesApi: vi.fn(),
}));

import {
  cerrarOtrasSesionesApi,
  cerrarSesionApi,
  listarMisSesionesApi,
} from './apiSesiones';
import { useCerrarOtrasSesiones, useCerrarSesion, useMisSesiones } from './useSesiones';
import type { SesionActiva } from './types';

const listarMock = vi.mocked(listarMisSesionesApi);
const cerrarMock = vi.mocked(cerrarSesionApi);
const cerrarOtrasMock = vi.mocked(cerrarOtrasSesionesApi);

beforeEach(() => {
  vi.clearAllMocks();
});

function _sesion(sid: string, esActual: boolean): SesionActiva {
  return {
    sid,
    ip: '127.0.0.1',
    user_agent: 'vitest',
    canal: true,
    inicio: '2026-07-10T10:00:00Z',
    last_activity: '2026-07-10T10:05:00Z',
    es_actual: esActual,
  };
}

describe('useMisSesiones', () => {
  it('expone las sesiones activas al resolverse', async () => {
    const sesiones = [_sesion('s1', true), _sesion('s2', false)];
    listarMock.mockResolvedValue(sesiones);

    const { Wrapper } = createQueryWrapper();
    const { result } = renderHook(() => useMisSesiones(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(sesiones);
    expect(listarMock).toHaveBeenCalledTimes(1);
  });

  it('expone el estado de error cuando la API rechaza', async () => {
    listarMock.mockRejectedValue(new Error('500'));

    const { Wrapper } = createQueryWrapper();
    const { result } = renderHook(() => useMisSesiones(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useCerrarSesion', () => {
  it('cierra la sesion por sid e invalida el listado', async () => {
    cerrarMock.mockResolvedValue(undefined);

    const { Wrapper, queryClient } = createQueryWrapper();
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

    const { result } = renderHook(() => useCerrarSesion(), { wrapper: Wrapper });
    result.current.mutate('s2');

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(cerrarMock).toHaveBeenCalledWith('s2');
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['sesiones-activas'] });
  });
});

describe('useCerrarOtrasSesiones', () => {
  it('cierra las demas sesiones e invalida el listado', async () => {
    cerrarOtrasMock.mockResolvedValue(undefined);

    const { Wrapper, queryClient } = createQueryWrapper();
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

    const { result } = renderHook(() => useCerrarOtrasSesiones(), { wrapper: Wrapper });
    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(cerrarOtrasMock).toHaveBeenCalledTimes(1);
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['sesiones-activas'] });
  });
});