import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';

// Mockeamos los hooks de mutación: el componente se prueba aislado de React Query.
// `solicitarMutate` invoca onSuccess para poder avanzar de paso en los tests.
const solicitarMutate = vi.fn();
const confirmarMutate = vi.fn();
const confirmarReset = vi.fn();
const useSolicitarMock = vi.fn();
const useConfirmarMock = vi.fn();

vi.mock('../model/useVerificacionEmail', () => ({
  useSolicitarCodigo: () => useSolicitarMock(),
  useConfirmarCodigo: () => useConfirmarMock(),
}));

import { VerificacionEmailForm } from './VerificacionEmailForm';

// El componente usa useSearchParams → necesita un Router. `ruta` permite simular
// el enlace del correo (?doc=&tipo=).
function renderForm(ruta = '/verificar-correo') {
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <VerificacionEmailForm />
    </MemoryRouter>,
  );
}

beforeEach(() => {
  solicitarMutate.mockReset();
  confirmarMutate.mockReset();
  confirmarReset.mockReset();
  useSolicitarMock.mockReturnValue({ mutate: solicitarMutate, isPending: false });
  useConfirmarMock.mockReturnValue({
    mutate: confirmarMutate,
    isPending: false,
    isError: false,
    error: null,
    reset: confirmarReset,
  });
});

describe('VerificacionEmailForm', () => {
  it('deshabilita "Enviar código" hasta tener al menos 3 dígitos de documento', async () => {
    const user = userEvent.setup();
    renderForm();

    const boton = screen.getByRole('button', { name: /enviar código/i });
    expect(boton).toBeDisabled();

    await user.type(screen.getByPlaceholderText('Solo números'), '12');
    expect(boton).toBeDisabled();

    await user.type(screen.getByPlaceholderText('Solo números'), '3');
    expect(boton).toBeEnabled();
  });

  it('solicita el código y avanza al paso de confirmación mostrando el correo enmascarado', async () => {
    solicitarMutate.mockImplementation((_payload, opts) => {
      opts?.onSuccess?.({
        enviado: true,
        mensaje: 'ok',
        email_enmascarado: 'j***@correo.com',
        expira_en_horas: 24,
      });
    });
    const user = userEvent.setup();
    renderForm();

    await user.type(screen.getByPlaceholderText('Solo números'), '1129565843');
    await user.click(screen.getByRole('button', { name: /enviar código/i }));

    expect(solicitarMutate).toHaveBeenCalledTimes(1);
    expect(solicitarMutate.mock.calls[0][0]).toEqual({
      tipo_documento: 'C.C.',
      numero_documento: '1129565843',
    });
    expect(await screen.findByText(/j\*\*\*@correo\.com/)).toBeInTheDocument();
  });

  it('en el paso de confirmación filtra no-dígitos y exige 8 dígitos para verificar', async () => {
    solicitarMutate.mockImplementation((_payload, opts) => {
      opts?.onSuccess?.({ enviado: true, mensaje: 'ok', email_enmascarado: null, expira_en_horas: 24 });
    });
    const user = userEvent.setup();
    renderForm();

    await user.type(screen.getByPlaceholderText('Solo números'), '123');
    await user.click(screen.getByRole('button', { name: /enviar código/i }));

    const input = await screen.findByPlaceholderText('8 dígitos');
    const verificar = screen.getByRole('button', { name: /verificar correo/i });
    expect(verificar).toBeDisabled();

    await user.type(input, '12ab34cd5678'); // se filtran letras → '12345678'
    expect(input).toHaveValue('12345678');
    expect(verificar).toBeEnabled();

    await user.click(verificar);
    expect(confirmarMutate).toHaveBeenCalledTimes(1);
    expect(confirmarMutate.mock.calls[0][0]).toEqual({
      tipo_documento: 'C.C.',
      numero_documento: '123',
      codigo: '12345678',
    });
  });

  it('con ?doc=&tipo= del correo aterriza directo en el paso de ingresar el código', async () => {
    const user = userEvent.setup();
    renderForm('/verificar-correo?doc=1129565843&tipo=C.C.');

    // Arranca en el paso de confirmar: hay campo de código, no de documento.
    const input = await screen.findByPlaceholderText('8 dígitos');
    expect(screen.queryByPlaceholderText('Solo números')).not.toBeInTheDocument();

    await user.type(input, '87654321');
    await user.click(screen.getByRole('button', { name: /verificar correo/i }));

    expect(confirmarMutate).toHaveBeenCalledTimes(1);
    expect(confirmarMutate.mock.calls[0][0]).toEqual({
      tipo_documento: 'C.C.',
      numero_documento: '1129565843',
      codigo: '87654321',
    });
  });
});
