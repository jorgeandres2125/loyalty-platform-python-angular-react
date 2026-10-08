import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Form, Button, Alert, Spinner, InputGroup } from 'react-bootstrap';
import { BrandLogo } from '../../shared/ui/components/BrandLogo';
import {
  cambiarPasswordTemporalApi,
  getMeApi,
} from '../../features/auth/model/apiAuth';
import { useAuthStore } from '../../entities/user/model/authStore';
import {
  PASSWORD_MIN_LENGTH,
  PASSWORD_MIN_CHAR_TYPES,
  contarTiposCaracter,
} from '../../shared/config/constants';

interface EstadoRuta {
  username?: string;
  expiraIso?: string;
}

// AP-0046: cambio obligatorio de la contrasena temporal tras su primer uso.
// Pagina publica (sin sesion): el usuario llega tras un login con estado 409.
export function CambioContrasenaTemporalPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const setAuth = useAuthStore((s) => s.setAuth);
  const estado = (location.state ?? {}) as EstadoRuta;

  const [username, setUsername] = useState(estado.username ?? '');
  const [passwordTemporal, setPasswordTemporal] = useState('');
  const [nuevaPassword, setNuevaPassword] = useState('');
  const [confirmarPassword, setConfirmarPassword] = useState('');
  const [mostrar, setMostrar] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(evento: React.FormEvent) {
    evento.preventDefault();
    setError(null);

    if (nuevaPassword.length < PASSWORD_MIN_LENGTH) {
      setError(`La nueva contrasena debe tener al menos ${PASSWORD_MIN_LENGTH} caracteres`);
      return;
    }
    if (contarTiposCaracter(nuevaPassword) < PASSWORD_MIN_CHAR_TYPES) {
      setError(
        `La contrasena debe contener al menos ${PASSWORD_MIN_CHAR_TYPES} de 4 tipos: ` +
          'minuscula, mayuscula, digito o caracter especial',
      );
      return;
    }
    if (nuevaPassword !== confirmarPassword) {
      setError('Las contrasenas no coinciden');
      return;
    }

    setLoading(true);
    try {
      await cambiarPasswordTemporalApi({
        username,
        password_temporal: passwordTemporal,
        nueva_password: nuevaPassword,
        confirmar_password: confirmarPassword,
      });
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
        'No se pudo cambiar la contrasena';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  }

  const tipo = mostrar ? 'text' : 'password';

  return (
    <div
      className="d-flex flex-column align-items-center justify-content-center min-vh-100 px-3"
      style={{ background: '#F4F5FA' }}
    >
      <div style={{ width: '100%', maxWidth: 460 }}>
        <div className="text-center mb-3">
          <BrandLogo height={32} />
        </div>
        <div className="bg-white rounded-4 shadow-sm p-4 p-md-5">
          <h4 className="fw-bold mb-1" style={{ color: '#100941' }}>
            Define tu contrasena personal
          </h4>
          <p className="text-muted mb-4" style={{ fontSize: '0.875rem' }}>
            Ingresaste con una contrasena temporal de un solo uso. Para continuar,
            crea ahora tu contrasena personal.
          </p>

          {error && (
            <Alert variant="danger" className="py-2 px-3" style={{ fontSize: '0.875rem' }}>
              <i className="bi bi-exclamation-circle me-2" />
              {error}
            </Alert>
          )}

          <Form onSubmit={handleSubmit} noValidate>
            <Form.Group className="mb-3">
              <Form.Label>Usuario</Form.Label>
              <Form.Control
                type="text"
                value={username}
                onChange={(evento) => setUsername(evento.target.value)}
                placeholder="Tu usuario"
                required
                disabled={loading}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Contrasena temporal</Form.Label>
              <Form.Control
                type={tipo}
                value={passwordTemporal}
                onChange={(evento) => setPasswordTemporal(evento.target.value)}
                autoComplete="one-time-code"
                placeholder="La contrasena temporal que recibiste"
                required
                disabled={loading}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Nueva contrasena</Form.Label>
              <InputGroup>
                <Form.Control
                  type={tipo}
                  value={nuevaPassword}
                  onChange={(evento) => setNuevaPassword(evento.target.value)}
                  placeholder={`Minimo ${PASSWORD_MIN_LENGTH} caracteres`}
                  minLength={PASSWORD_MIN_LENGTH}
                  required
                  disabled={loading}
                />
                <Button
                  variant="outline-secondary"
                  type="button"
                  onClick={() => setMostrar((p) => !p)}
                  tabIndex={-1}
                  aria-label={mostrar ? 'Ocultar contrasenas' : 'Mostrar contrasenas'}
                >
                  <i className={`bi ${mostrar ? 'bi-eye-slash' : 'bi-eye'}`} />
                </Button>
              </InputGroup>
            </Form.Group>

            <Form.Group className="mb-4">
              <Form.Label>Confirmar nueva contrasena</Form.Label>
              <Form.Control
                type={tipo}
                value={confirmarPassword}
                onChange={(evento) => setConfirmarPassword(evento.target.value)}
                placeholder="Repite la nueva contrasena"
                minLength={PASSWORD_MIN_LENGTH}
                required
                disabled={loading}
              />
            </Form.Group>

            <Button
              type="submit"
              variant="primary"
              className="w-100 py-2"
              disabled={
                loading ||
                !username ||
                !passwordTemporal ||
                !nuevaPassword ||
                !confirmarPassword
              }
            >
              {loading ? (
                <>
                  <Spinner size="sm" className="me-2" />
                  Guardando…
                </>
              ) : (
                <>
                  <i className="bi bi-shield-lock me-2" />
                  Crear contrasena e ingresar
                </>
              )}
            </Button>
          </Form>
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
