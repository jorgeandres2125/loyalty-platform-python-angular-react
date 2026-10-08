import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { createQueryWrapper } from '../../../test/queryWrapper';

// Mockeamos el módulo de API: el hook se prueba de forma aislada, sin red.
vi.mock('./apiAdminAfp', () => ({
  listarAdminAfpApi: vi.fn(),
  crearAdminAfpApi: vi.fn(),
  actualizarAdminAfpApi: vi.fn(),
  eliminarAdminAfpApi: vi.fn(),
}));

import {
  listarAdminAfpApi,
  crearAdminAfpApi,
} from './apiAdminAfp';
import { useAdminAfpList, useCrearAdminAfp } from './useAdminAfp';
import type { AdminAfpListResponse, AdminAfpFormResponse } from './types';

const listarMock = vi.mocked(listarAdminAfpApi);
const crearMock = vi.mocked(crearAdminAfpApi);

beforeEach(() => {
  vi.clearAllMocks();
});

describe('useAdminAfpList', () => {
  it('llama a la API con el query y expone los datos al resolverse', async () => {
    const respuesta: AdminAfpListResponse = {
      items: [{ tid: 1, nombre: 'Porvenir', nit: '800123' }],
      total: 1,
      page: 1,
      page_size: 10,
    };
    listarMock.mockResolvedValue(respuesta);

    const { Wrapper } = createQueryWrapper();
    const query = { page: 1, page_size: 10 };
    const { result } = renderHook(() => useAdminAfpList(query), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(respuesta);
    expect(listarMock).toHaveBeenCalledWith(query);
  });

  it('expone el estado de error cuando la API rechaza', async () => {
    listarMock.mockRejectedValue(new Error('500'));

    const { Wrapper } = createQueryWrapper();
    const { result } = renderHook(
      () => useAdminAfpList({ page: 1, page_size: 10 }),
      { wrapper: Wrapper },
    );

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useCrearAdminAfp', () => {
  it('crea el registro e invalida la query de listado', async () => {
    const creado: AdminAfpFormResponse = { tid: 9, nombre: 'Colfondos', nit: '900' };
    crearMock.mockResolvedValue(creado);

    const { Wrapper, queryClient } = createQueryWrapper();
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

    const { result } = renderHook(() => useCrearAdminAfp(), { wrapper: Wrapper });
    result.current.mutate({ nombre: 'Colfondos', nit: '900' });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(crearMock).toHaveBeenCalledWith({ nombre: 'Colfondos', nit: '900' });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['admin-afp-list'] });
    expect(result.current.data).toEqual(creado);
  });
});
