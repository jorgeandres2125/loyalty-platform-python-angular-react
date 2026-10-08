import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Form, Button, Alert, Spinner, InputGroup } from 'react-bootstrap';
import { BrandLogo } from '../../shared/ui/components/BrandLogo';
import {
  cambiarPasswordExpiradaApi,
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
  diasRestantesGracia?: number;
}

const BARRA = String.fromCharCode(47);

// AP-0038: cambio autonomo de una contrasena vencida dentro de la ventana de gracia.
// Pagina publica (sin sesion): el usuario llega tras un login con estado 409.
export function CambioContrasenaVencidaPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const setAuth = useAuthStore((s) => s.setAuth);
  const estado = (location.state ?? {}) as EstadoRuta;

  const [username, setUsername] = useState(estado.username ?? '');
  const [passwordActual, setPasswordActual] = useState('');
  const [nuevaPassword, setNuevaPassword] = useState('');
  const [confirmarPassword, setConfirmarPassword] = useState('');
  const [mostrar, setMostrar] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (nuevaPassword.length < PASSWORD_MIN_LENGTH) {
      setError(`La nueva contraseña debe tener al menos ${PASSWORD_MIN_LENGTH} caracteres`);
      return;
    }
    if (contarTiposCaracter(nuevaPassword) < PASSWORD_MIN_CHAR_TYPES) {
      setError(
        `La contraseña debe contener al menos ${PASSWORD_MIN_CHAR_TYPES} de 4 tipos: ` +
          'minúscula, mayúscula, dígito o carácter especial',
      );
      return;
    }
    if (nuevaPassword !== confirmarPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    setLoading(true);
    try {
      await cambiarPasswordExpiradaApi({
        username,
        password_actual: passwordActual,
        nueva_password: nuevaPassword,
        confirmar_password: confirmarPassword,
      });
      const user = await getMeApi();
      setAuth(user);
      const destino: string =
        [...(user.modulos ?? [])]
          .filter((m) => m.puede_ver && m.ruta)
          .sort((a, b) => a.orden - b.orden)[0]?.ruta ?? BARRA + 'dashboard';
      navigate(destino, { replace: true });
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'No se pudo cambiar la contraseña';
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
            Tu contraseña venció
          </h4>
          <p className="text-muted mb-4" style={{ fontSize: '0.875rem' }}>
            Puedes actualizarla de forma autónoma durante el periodo de gracia.
            {typeof estado.diasRestantesGracia === 'number' && (
              <> Te quedan {estado.diasRestantesGracia} día(s).</>
            )}
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
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Tu usuario"
                required
                disabled={loading}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Contraseña actual (vencida)</Form.Label>
              <Form.Control
                type={tipo}
                value={passwordActual}
                onChange={(e) => setPasswordActual(e.target.value)}
                autoComplete="current-password"
                placeholder="Tu contraseña actual"
                required
                disabled={loading}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Nueva contraseña</Form.Label>
              <InputGroup>
                <Form.Control
                  type={tipo}
                  value={nuevaPassword}
                  onChange={(e) => setNuevaPassword(e.target.value)}
                  placeholder={`Mínimo ${PASSWORD_MIN_LENGTH} caracteres`}
                  minLength={PASSWORD_MIN_LENGTH}
                  required
                  disabled={loading}
                />
                <Button
                  variant="outline-secondary"
                  type="button"
                  onClick={() => setMostrar((p) => !p)}
                  tabIndex={-1}
                  aria-label={mostrar ? 'Ocultar contraseñas' : 'Mostrar contraseñas'}
                >
                  <i className={`bi ${mostrar ? 'bi-eye-slash' : 'bi-eye'}`} />
                </Button>
              </InputGroup>
            </Form.Group>

            <Form.Group className="mb-4">
              <Form.Label>Confirmar nueva contraseña</Form.Label>
              <Form.Control
                type={tipo}
                value={confirmarPassword}
                onChange={(e) => setConfirmarPassword(e.target.value)}
                placeholder="Repite la nueva contraseña"
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
                !passwordActual ||
                !nuevaPassword ||
                !confirmarPassword
              }
            >
              {loading ? (
                <>
                  <Spinner size="sm" className="me-2" />
                  Actualizando…
                </>
              ) : (
                <>
                  <i className="bi bi-shield-lock me-2" />
                  Cambiar contraseña e ingresar
                </>
              )}
            </Button>
          </Form>
        </div>
        <div className="text-center mt-3">
          <Link
            to={BARRA + 'login'}
            className="text-decoration-none text-muted"
            style={{ fontSize: '0.85rem' }}
          >
            <i className="bi bi-arrow-left me-1" />
            Volver al inicio de sesión
          </Link>
        </div>
      </div>
    </div>
  );
}
