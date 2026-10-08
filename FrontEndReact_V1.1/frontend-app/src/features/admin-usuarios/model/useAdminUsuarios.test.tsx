import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { createQueryWrapper } from '../../../test/queryWrapper';

// Mockeamos el módulo de API: los hooks se prueban aislados, sin red.
vi.mock('./apiAdminUsuarios', () => ({
  listarUsuariosApi: vi.fn(),
  cambiarEstadoUsuarioApi: vi.fn(),
  cambiarEstadoComisionistaApi: vi.fn(),
}));

import {
  listarUsuariosApi,
  cambiarEstadoUsuarioApi,
  cambiarEstadoComisionistaApi,
} from './apiAdminUsuarios';
import {
  useAdminUsuariosList,
  useCambiarEstadoUsuario,
  useCambiarEstadoComisionista,
} from './useAdminUsuarios';
import type { UsuarioListItem, UsuarioListResponse } from './types';

const listarMock = vi.mocked(listarUsuariosApi);
const cambiarUsuarioMock = vi.mocked(cambiarEstadoUsuarioApi);
const cambiarComisionistaMock = vi.mocked(cambiarEstadoComisionistaApi);

beforeEach(() => {
  vi.clearAllMocks();
});

describe('useAdminUsuariosList', () => {
  it('llama a la API con el query y expone los datos al resolverse', async () => {
    const respuesta: UsuarioListResponse = {
      items: [
        { uid: 700, nombre: 'jperez', email: 'j@sufi.co', activo: true, roles: ['comisionista'] },
      ],
      total: 1,
      page: 1,
      page_size: 10,
    };
    listarMock.mockResolvedValue(respuesta);

    const { Wrapper } = createQueryWrapper();
    const query = { page: 1, page_size: 10, activo: true };
    const { result } = renderHook(() => useAdminUsuariosList(query), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(respuesta);
    expect(listarMock).toHaveBeenCalledWith(query);
  });

  it('expone el estado de error cuando la API rechaza', async () => {
    listarMock.mockRejectedValue(new Error('500'));

    const { Wrapper } = createQueryWrapper();
    const { result } = renderHook(
      () => useAdminUsuariosList({ page: 1, page_size: 10 }),
      { wrapper: Wrapper },
    );

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useCambiarEstadoUsuario', () => {
  it('cambia el estado e invalida la query de listado', async () => {
    const item: UsuarioListItem = {
      uid: 700,
      nombre: 'jperez',
      email: 'j@sufi.co',
      activo: false,
      roles: ['comisionista'],
    };
    cambiarUsuarioMock.mockResolvedValue(item);

    const { Wrapper, queryClient } = createQueryWrapper();
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

    const { result } = renderHook(() => useCambiarEstadoUsuario(), { wrapper: Wrapper });
    result.current.mutate({ uid: 700, payload: { activo: false } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(cambiarUsuarioMock).toHaveBeenCalledWith(700, { activo: false });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['admin-usuarios-list'] });
    expect(result.current.data).toEqual(item);
  });
});

describe('useCambiarEstadoComisionista', () => {
  it('deshabilita la cuenta del comisionista por documento y programa', async () => {
    const item: UsuarioListItem = {
      uid: 700,
      nombre: '22544953',
      email: 'c@sufi.co',
      activo: false,
      roles: ['comisionista_consumo'],
    };
    cambiarComisionistaMock.mockResolvedValue(item);

    const { Wrapper } = createQueryWrapper();
    const { result } = renderHook(() => useCambiarEstadoComisionista(), { wrapper: Wrapper });
    result.current.mutate({
      programa: 'consumo',
      numeroDocumento: '22544953',
      payload: { activo: false },
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(cambiarComisionistaMock).toHaveBeenCalledWith('consumo', '22544953', {
      activo: false,
    });
    expect(result.current.data).toEqual(item);
  });
});
