import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <div className="d-flex flex-column align-items-center justify-content-center text-center" style={{ minHeight: '70vh' }}>
      <div style={{ fontSize: '5rem', fontWeight: 800, color: '#FF0026', lineHeight: 1 }}>404</div>
      <h4 className="mt-3 fw-bold" style={{ color: '#333241' }}>Página no encontrada</h4>
      <p className="text-muted mb-4">La URL que ingresaste no existe o no tienes permiso de acceso.</p>
      <Link to="/dashboard" className="btn btn-primary">
        <i className="bi bi-house me-2" />
        Ir al Dashboard
      </Link>
    </div>
  );
}
