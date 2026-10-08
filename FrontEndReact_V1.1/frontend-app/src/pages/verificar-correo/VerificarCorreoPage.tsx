import { Link } from 'react-router-dom';
import { BrandLogo } from '../../shared/ui/components/BrandLogo';
import { VerificacionEmailForm } from '../../features/verificacion-email/ui/VerificacionEmailForm';

export function VerificarCorreoPage() {
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
          <VerificacionEmailForm />
        </div>
        <div className="text-center mt-3">
          <Link
            to="/login"
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
