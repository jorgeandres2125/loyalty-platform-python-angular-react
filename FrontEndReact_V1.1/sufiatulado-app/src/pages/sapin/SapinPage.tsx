import { useSapinToken } from '../../features/sapin/model/useSapinToken';
import { useAuthStore } from '../../entities/user/model/authStore';
import { LoadingSpinner } from '../../shared/ui/components/LoadingSpinner';
import { PageHeader } from '../../shared/ui/components/PageHeader';

export function SapinPage() {
  const canAccess = useAuthStore((s) => s.canAccessSapin());
  const { data, isLoading, error } = useSapinToken();

  if (!canAccess) {
    return (
      <div>
        <PageHeader title="Incentivos SAPIN" icon="bi-stars" />
        <div className="text-center py-5">
          <i className="bi bi-lock-fill text-muted" style={{ fontSize: '3rem' }} />
          <h5 className="mt-3 text-muted">Acceso restringido</h5>
          <p className="text-muted small">No tienes acceso a los incentivos SAPIN.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Incentivos SAPIN"
        subtitle="Plataforma de incentivos y recompensas"
        icon="bi-stars"
      />

      {isLoading && <LoadingSpinner fullPage text="Cargando plataforma SAPIN..." />}

      {error && (
        <div className="alert alert-warning">
          <i className="bi bi-exclamation-triangle me-2" />
          No se pudo cargar la plataforma SAPIN. Intenta de nuevo.
        </div>
      )}

      {data && (
        <div className="bg-white rounded-3 shadow-sm overflow-hidden" style={{ minHeight: '75vh' }}>
          <div className="p-3 border-bottom d-flex align-items-center justify-content-between">
            <div className="d-flex align-items-center gap-2">
              <i className="bi bi-stars text-warning" />
              <span className="fw-semibold small">Portal de Incentivos SAPIN</span>
            </div>
            <a
              href={data.sapin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-sm btn-outline-primary"
            >
              <i className="bi bi-box-arrow-up-right me-1" />
              Abrir en nueva ventana
            </a>
          </div>
          <iframe
            src={`${data.sapin_url}?token=${data.token}`}
            title="Portal SAPIN"
            width="100%"
            style={{ height: 'calc(75vh - 56px)', border: 'none' }}
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          />
        </div>
      )}
    </div>
  );
}
