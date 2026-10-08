import { useState, useEffect } from 'react';
import axios from 'axios';
import { Form, Button, Alert, InputGroup } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useLogin } from '../model/useLogin';
import { useFormTimeout } from '../../../shared/lib/useFormTimeout';
import { AUTH_FORM_TIMEOUT_MS } from '../../../shared/config/constants';

import type { OtpDesafio } from '../../../entities/user/model/types';

const LOGIN_ERROR_VISIBLE_MS = 10000;

function mensajeDeError(error: unknown): string {
  const generico = 'Credenciales inválidas. Intenta de nuevo.';
  if (axios.isAxiosError(error)) {
    const detalle = error.response?.data?.detail;
    if (typeof detalle === 'string' && detalle.trim().length > 0) {
      return detalle;
    }
  }
  return generico;
}

export function LoginForm() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [expirado, setExpirado] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [otpDesafio, setOtpDesafio] = useState<OtpDesafio | null>(null);
  const { mutate: login, isPending, error, data } = useLogin();

  useEffect(() => {
    if (!error) {
      return;
    }
    setErrorMsg(mensajeDeError(error));
    const id = window.setTimeout(() => setErrorMsg(null), LOGIN_ERROR_VISIBLE_MS);
    return () => window.clearTimeout(id);
  }, [error]);

  // AP-0012: cuando el backend exige OTP guardamos el desafio para mostrar
  // el enlace de ingreso del codigo. El mensaje se muestra en el toast.
  useEffect(() => {
    if (data && data.kind === 'otp') {
      setOtpDesafio(data.desafio);
      setErrorMsg(null);
    }
  }, [data]);

  // AP-0018: límite absoluto de 1 min desde la primera interacción. Vencido el
  // plazo sin enviar, se borran las credenciales tecleadas.
  const hayInteraccion: boolean = username.length > 0 || password.length > 0;
  useFormTimeout({
    delayMs: AUTH_FORM_TIMEOUT_MS,
    active: hayInteraccion && !isPending,
    onTimeout: () => {
      setUsername('');
      setPassword('');
      setShowPass(false);
      setExpirado(true);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorMsg(null);
    setOtpDesafio(null);
    login({ username, password });
  }

  function irAlOtp() {
    if (otpDesafio) {
      navigate('/login/otp', { state: { desafio: otpDesafio } });
    }
  }

  return (
    <Form onSubmit={handleSubmit} noValidate style={{ width: '100%' }}>
      <h4 className="fw-bold mb-1" style={{ color: '#100941' }}>Iniciar sesión</h4>
      <p className="text-muted mb-4" style={{ fontSize: '0.875rem' }}>
        Accede a tu plataforma SUFI Contigo
      </p>

      {errorMsg && (
        <Alert variant="danger" className="py-2 px-3" style={{ fontSize: '0.875rem' }}>
          <i className="bi bi-exclamation-circle me-2" />
          {errorMsg}
        </Alert>
      )}

      {otpDesafio && (
        <Alert variant="info" className="py-2 px-3" style={{ fontSize: '0.875rem' }}>
          <i className="bi bi-shield-lock me-2" />
          {otpDesafio.mensaje}
          {otpDesafio.emailEnmascarado && (
            <span className="d-block text-muted mt-1">
              Codigo enviado a {otpDesafio.emailEnmascarado}
            </span>
          )}
          <div className="mt-2">
            <Button variant="primary" size="sm" type="button" onClick={irAlOtp}>
              <i className="bi bi-key me-1" />
              Ingresar codigo de acceso
            </Button>
          </div>
        </Alert>
      )}

      {expirado && (
        <Alert variant="warning" className="py-2 px-3" style={{ fontSize: '0.875rem' }}>
          <i className="bi bi-clock-history me-2" />
          Por seguridad se limpiaron tus datos tras 1 minuto sin enviarlos. Ingrésalos de nuevo.
        </Alert>
      )}

      <Form.Group className="mb-3">
        <Form.Label>Usuario</Form.Label>
        <InputGroup>
          <InputGroup.Text className="bg-light border-end-0">
            <i className="bi bi-person text-muted" />
          </InputGroup.Text>
          <Form.Control
            type="text"
            placeholder="Tu usuario"
            value={username}
            onChange={(e) => {
              setUsername(e.target.value);
              setExpirado(false);
            }}
            required
            autoFocus
            className="border-start-0"
          />
        </InputGroup>
      </Form.Group>

      <Form.Group className="mb-4">
        <Form.Label>Contraseña</Form.Label>
        <InputGroup>
          <InputGroup.Text className="bg-light border-end-0">
            <i className="bi bi-lock text-muted" />
          </InputGroup.Text>
          <Form.Control
            type={showPass ? 'text' : 'password'}
            placeholder="Tu contraseña"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setExpirado(false);
            }}
            required
            className="border-start-0 border-end-0"
          />
          <Button
            variant="light"
            className="border"
            type="button"
            onClick={() => setShowPass((p) => !p)}
            tabIndex={-1}
            aria-label={showPass ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          >
            <i className={`bi bi-eye${showPass ? '-slash' : ''} text-muted`} />
          </Button>
        </InputGroup>
      </Form.Group>

      <Button
        type="submit"
        variant="primary"
        className="w-100 py-2"
        disabled={isPending || !username || !password}
      >
        {isPending ? (
          <>
            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
            Ingresando...
          </>
        ) : (
          <>
            <i className="bi bi-box-arrow-in-right me-2" />
            Ingresar
          </>
        )}
      </Button>

      <div className="text-center mt-3">
        <Link
          to="/verificar-correo"
          className="text-decoration-none"
          style={{ fontSize: '0.85rem' }}
        >
          <i className="bi bi-envelope-check me-1" />
          Verificar mi correo electrónico
        </Link>
      </div>
    </Form>
  );
}
