import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Alert, Spinner, InputGroup } from 'react-bootstrap';
import { apiClient } from '../../shared/api/client';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { useFormTimeout } from '../../shared/lib/useFormTimeout';
import {
  AUTH_FORM_TIMEOUT_MS,
  PASSWORD_MIN_LENGTH,
  PASSWORD_MIN_CHAR_TYPES,
  contarTiposCaracter,
} from '../../shared/config/constants';

export function CambioContrasenaPage() {
  const navigate = useNavigate();
  const [passwordActual, setPasswordActual] = useState('');
  const [nuevaPassword, setNuevaPassword] = useState('');
  const [confirmarPassword, setConfirmarPassword] = useState('');
  const [showActual, setShowActual] = useState(false);
  const [showNueva, setShowNueva] = useState(false);
  const [showConfirmar, setShowConfirmar] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState(false);
  const [expirado, setExpirado] = useState(false);

  // AP-0018: límite absoluto de 1 min desde la primera interacción. Vencido el
  // plazo sin enviar, se borran las contraseñas tecleadas.
  const hayInteraccion: boolean =
    passwordActual.length > 0 || nuevaPassword.length > 0 || confirmarPassword.length > 0;
  useFormTimeout({
    delayMs: AUTH_FORM_TIMEOUT_MS,
    active: hayInteraccion && !loading && !exito,
    onTimeout: () => {
      setPasswordActual('');
      setNuevaPassword('');
      setConfirmarPassword('');
      setShowActual(false);
      setShowNueva(false);
      setShowConfirmar(false);
      setError(null);
      setExpirado(true);
    },
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    // AP-0044: política de longitud mínima para usuarios finales.
    if (nuevaPassword.length < PASSWORD_MIN_LENGTH) {
      setError(`La nueva contraseña debe tener al menos ${PASSWORD_MIN_LENGTH} caracteres`);
      return;
    }

    // AP-0051: complejidad — al menos 3 de los 4 tipos de carácter.
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
      await apiClient.patch('/auth/password', {
        password_actual: passwordActual,
        nueva_password: nuevaPassword,
        confirmar_password: confirmarPassword,
      });
      setExito(true);
      setTimeout(() => navigate('/configuraciones'), 2000);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Error al cambiar la contraseña';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="cambio-contrasena-page">
      <PageHeader
        title="Cambiar Contraseña"
        icon="bi-lock-fill"
        backTo="/configuraciones"
      />

      <div className="cambio-contrasena-page__card">
        {exito ? (
          <Alert variant="success" className="text-center mb-0">
            <i className="bi bi-check-circle-fill me-2" />
            Contraseña actualizada correctamente. Redirigiendo…
          </Alert>
        ) : (
          <Form onSubmit={handleSubmit} noValidate>
            {error && (
              <Alert variant="danger" onClose={() => setError(null)} dismissible>
                <i className="bi bi-exclamation-circle me-2" />
                {error}
              </Alert>
            )}

            {expirado && (
              <Alert variant="warning">
                <i className="bi bi-clock-history me-2" />
                Por seguridad se limpiaron los datos tras 1 minuto sin enviarlos. Ingrésalos de nuevo.
              </Alert>
            )}

            <Form.Group className="mb-3" controlId="passwordActual">
              <Form.Label className="cambio-contrasena-page__label">
                Contraseña Actual
              </Form.Label>
              <InputGroup>
                <Form.Control
                  type={showActual ? 'text' : 'password'}
                  value={passwordActual}
                  onChange={(e) => {
                    setPasswordActual(e.target.value);
                    setExpirado(false);
                  }}
                  placeholder="Tu contraseña actual"
                  autoComplete="current-password"
                  required
                  disabled={loading}
                />
                <Button
                  variant="outline-secondary"
                  onClick={() => setShowActual((p) => !p)}
                  tabIndex={-1}
                  aria-label={showActual ? 'Ocultar contraseña actual' : 'Mostrar contraseña actual'}
                >
                  <i className={`bi ${showActual ? 'bi-eye-slash' : 'bi-eye'}`} />
                </Button>
              </InputGroup>
            </Form.Group>

            <Form.Group className="mb-3" controlId="nuevaPassword">
              <Form.Label className="cambio-contrasena-page__label">
                Nueva Contraseña
              </Form.Label>
              <InputGroup>
                <Form.Control
                  type={showNueva ? 'text' : 'password'}
                  value={nuevaPassword}
                  onChange={(e) => {
                    setNuevaPassword(e.target.value);
                    setExpirado(false);
                  }}
                  placeholder={`Mínimo ${PASSWORD_MIN_LENGTH} caracteres`}
                  required
                  minLength={PASSWORD_MIN_LENGTH}
                  disabled={loading}
                />
                <Button
                  variant="outline-secondary"
                  onClick={() => setShowNueva((p) => !p)}
                  tabIndex={-1}
                >
                  <i className={`bi ${showNueva ? 'bi-eye-slash' : 'bi-eye'}`} />
                </Button>
              </InputGroup>
            </Form.Group>

            <Form.Group className="mb-4" controlId="confirmarPassword">
              <Form.Label className="cambio-contrasena-page__label">
                Confirmar Nueva Contraseña
              </Form.Label>
              <InputGroup>
                <Form.Control
                  type={showConfirmar ? 'text' : 'password'}
                  value={confirmarPassword}
                  onChange={(e) => {
                    setConfirmarPassword(e.target.value);
                    setExpirado(false);
                  }}
                  placeholder="Repite la nueva contraseña"
                  required
                  minLength={PASSWORD_MIN_LENGTH}
                  disabled={loading}
                />
                <Button
                  variant="outline-secondary"
                  onClick={() => setShowConfirmar((p) => !p)}
                  tabIndex={-1}
                >
                  <i className={`bi ${showConfirmar ? 'bi-eye-slash' : 'bi-eye'}`} />
                </Button>
              </InputGroup>
            </Form.Group>

            <Button
              type="submit"
              className="w-100 cambio-contrasena-page__submit"
              disabled={loading || !passwordActual || !nuevaPassword || !confirmarPassword}
            >
              {loading ? (
                <>
                  <Spinner size="sm" className="me-2" />
                  Actualizando…
                </>
              ) : (
                <>
                  <i className="bi bi-check-lg me-2" />
                  Actualizar Contraseña
                </>
              )}
            </Button>
          </Form>
        )}
      </div>
    </div>
  );
}
