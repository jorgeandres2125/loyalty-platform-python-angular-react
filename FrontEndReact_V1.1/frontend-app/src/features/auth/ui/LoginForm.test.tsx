import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';

// Mockeamos el hook de login: el componente se prueba aislado de React Query
// y del router. `useLoginMock` deja inyectar mutate/isPending/error por test.
const loginMutate = vi.fn();
const useLoginMock = vi.fn();
vi.mock('../model/useLogin', () => ({
  useLogin: () => useLoginMock(),
}));

import { LoginForm } from './LoginForm';

// El componente incluye un <Link> a /verificar-correo → necesita un Router.
function renderForm() {
  return render(
    <MemoryRouter>
      <LoginForm />
    </MemoryRouter>,
  );
}

beforeEach(() => {
  loginMutate.mockReset();
  useLoginMock.mockReturnValue({ mutate: loginMutate, isPending: false, error: null });
});

afterEach(() => {
  vi.useRealTimers();
});

describe('LoginForm', () => {
  it('deshabilita el botón hasta que usuario y contraseña tienen valor', async () => {
    const user = userEvent.setup();
    renderForm();

    const boton = screen.getByRole('button', { name: /ingresar/i });
    expect(boton).toBeDisabled();

    await user.type(screen.getByPlaceholderText('Tu usuario'), 'jdoe');
    expect(boton).toBeDisabled(); // falta la contraseña

    await user.type(screen.getByPlaceholderText('Tu contraseña'), 'secreto');
    expect(boton).toBeEnabled();
  });

  it('envía las credenciales al hacer submit', async () => {
    const user = userEvent.setup();
    renderForm();

    await user.type(screen.getByPlaceholderText('Tu usuario'), 'jdoe');
    await user.type(screen.getByPlaceholderText('Tu contraseña'), 'secreto');
    await user.click(screen.getByRole('button', { name: /ingresar/i }));

    expect(loginMutate).toHaveBeenCalledTimes(1);
    expect(loginMutate).toHaveBeenCalledWith({ username: 'jdoe', password: 'secreto' });
  });

  it('alterna la visibilidad de la contraseña', async () => {
    const user = userEvent.setup();
    renderForm();

    const pass = screen.getByPlaceholderText('Tu contraseña');
    expect(pass).toHaveAttribute('type', 'password');

    await user.click(screen.getByRole('button', { name: /mostrar contraseña/i }));
    expect(pass).toHaveAttribute('type', 'text');

    await user.click(screen.getByRole('button', { name: /ocultar contraseña/i }));
    expect(pass).toHaveAttribute('type', 'password');
  });

  it('muestra la alerta de credenciales inválidas cuando hay error', () => {
    useLoginMock.mockReturnValue({
      mutate: loginMutate,
      isPending: false,
      error: new Error('401'),
    });
    renderForm();

    expect(screen.getByText(/credenciales inválidas/i)).toBeInTheDocument();
  });

  it('muestra el estado de carga y deshabilita el botón mientras isPending', () => {
    useLoginMock.mockReturnValue({ mutate: loginMutate, isPending: true, error: null });
    renderForm();

    expect(screen.getByRole('button', { name: /ingresando/i })).toBeDisabled();
  });

  // Con fake timers se usa fireEvent (síncrono): userEvent agenda delays internos
  // que se bloquean contra los temporizadores falsos.
  it('AP-0018: borra las credenciales y avisa tras 1 minuto sin enviarlas', () => {
    vi.useFakeTimers();
    renderForm();

    fireEvent.change(screen.getByPlaceholderText('Tu usuario'), { target: { value: 'jdoe' } });
    fireEvent.change(screen.getByPlaceholderText('Tu contraseña'), { target: { value: 'secreto' } });
    expect(screen.getByPlaceholderText('Tu usuario')).toHaveValue('jdoe');

    act(() => vi.advanceTimersByTime(60_000));

    expect(screen.getByPlaceholderText('Tu usuario')).toHaveValue('');
    expect(screen.getByPlaceholderText('Tu contraseña')).toHaveValue('');
    expect(screen.getByText(/se limpiaron tus datos tras 1 minuto/i)).toBeInTheDocument();
  });

  it('AP-0018: no borra las credenciales antes del minuto', () => {
    vi.useFakeTimers();
    renderForm();

    fireEvent.change(screen.getByPlaceholderText('Tu usuario'), { target: { value: 'jdoe' } });
    act(() => vi.advanceTimersByTime(59_000));

    expect(screen.getByPlaceholderText('Tu usuario')).toHaveValue('jdoe');
  });
});
