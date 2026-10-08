import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';
import { BrandLogo } from '../../shared/ui/components/BrandLogo';
import { completarLoginOtpApi, getMeApi } from '../../features/auth/model/apiAuth';
import { useAuthStore } from '../../entities/user/model/authStore';
import type { OtpDesafio } from '../../entities/user/model/types';

interface EstadoRuta {
  desafio?: OtpDesafio;
}

// AP-0012: segundo paso del login. El usuario ingresa el codigo OTP de un
// solo uso recibido por correo. Pagina publica: se llega tras un login 202.
export function LoginOtpPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const setAuth = useAuthStore((s) => s.setAuth);
  const estado = (location.state ?? {}) as EstadoRuta;
  const desafio = estado.desafio;

  const [codigo, setCodigo] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(evento: React.FormEvent) {
    evento.preventDefault();
    setError(null);
    if (!desafio) {
      return;
    }
    if (codigo.length !== 6) {
      setError('El codigo debe tener 6 digitos.');
      return;
    }
    setLoading(true);
    try {
      await completarLoginOtpApi({ desafio_id: desafio.desafioId, codigo });
      const user = await getMeApi();
      setAuth(user);
      const destino: string =
        [...(user.modulos ?? [])]
          .filter((m) => m.puede_ver && m.ruta)
          .sort((a, b) => a.orden - b.orden)[0]?.ruta ?? '/dashboard';
      navigate(destino, { replace: true });
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'No se pudo verificar el codigo. Intenta de nuevo.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  }

  function manejarCodigo(evento: React.ChangeEvent<HTMLInputElement>) {
    const soloDigitos = [...evento.target.value]
      .filter((c) => c >= '0' && c <= '9')
      .join('')
      .slice(0, 6);
    setCodigo(soloDigitos);
  }

  return (
    <div
      className="d-flex flex-column align-items-center justify-content-center min-vh-100 px-3"
      style={{ background: '#F4F5FA' }}
    >
      <div style={{ width: '100%', maxWidth: 440 }}>
        <div className="text-center mb-3">
          <BrandLogo height={32} />
        </div>
        <div className="bg-white rounded-4 shadow-sm p-4 p-md-5">
          <h4 className="fw-bold mb-1" style={{ color: '#100941' }}>
            Verificacion en dos pasos
          </h4>
          <p className="text-muted mb-4" style={{ fontSize: '0.875rem' }}>
            Ingresa el codigo de acceso de un solo uso que enviamos a tu correo.
          </p>

          {!desafio && (
            <Alert variant="warning" className="py-2 px-3" style={{ fontSize: '0.875rem' }}>
              <i className="bi bi-exclamation-triangle me-2" />
              No hay un desafio activo. Inicia sesion de nuevo para recibir un codigo.
            </Alert>
          )}

          {error && (
            <Alert variant="danger" className="py-2 px-3" style={{ fontSize: '0.875rem' }}>
              <i className="bi bi-exclamation-circle me-2" />
              {error}
            </Alert>
          )}

          {desafio && (
            <Form onSubmit={handleSubmit} noValidate>
              {desafio.emailEnmascarado && (
                <p className="text-muted mb-3" style={{ fontSize: '0.85rem' }}>
                  <i className="bi bi-envelope me-1" />
                  Codigo enviado a <strong>{desafio.emailEnmascarado}</strong>
                </p>
              )}
              <Form.Group className="mb-4">
                <Form.Label>Codigo de acceso</Form.Label>
                <Form.Control
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  value={codigo}
                  onChange={manejarCodigo}
                  placeholder="6 digitos"
                  autoFocus
                  required
                  disabled={loading}
                />
              </Form.Group>
              <Button
                type="submit"
                variant="primary"
                className="w-100 py-2"
                disabled={loading || codigo.length !== 6}
              >
                {loading ? (
                  <>
                    <Spinner size="sm" className="me-2" />
                    Verificando...
                  </>
                ) : (
                  <>
                    <i className="bi bi-shield-check me-2" />
                    Verificar e ingresar
                  </>
                )}
              </Button>
            </Form>
          )}
        </div>
        <div className="text-center mt-3">
          <Link
            to={'/login'}
            className="text-decoration-none text-muted"
            style={{ fontSize: '0.85rem' }}
          >
            <i className="bi bi-arrow-left me-1" />
            Volver al inicio de sesion
          </Link>
        </div>
      </div>
    </div>
  );
}
