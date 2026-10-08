interface Props {
  error?: Error;
  resetErrorBoundary?: () => void;
}

export function ErrorBoundaryFallback({ error, resetErrorBoundary }: Props) {
  return (
    <div className="d-flex flex-column align-items-center justify-content-center py-5 px-4 text-center">
      <i className="bi bi-exclamation-triangle-fill text-warning" style={{ fontSize: '3rem' }} />
      <h5 className="mt-3 fw-bold">Ocurrió un error</h5>
      <p className="text-muted small mb-3">{error?.message ?? 'Error inesperado'}</p>
      {resetErrorBoundary && (
        <button className="btn btn-outline-primary btn-sm" onClick={resetErrorBoundary}>
          <i className="bi bi-arrow-clockwise me-1" />
          Reintentar
        </button>
      )}
    </div>
  );
}
