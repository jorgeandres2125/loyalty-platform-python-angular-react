interface Props {
  fullPage?: boolean;
  text?: string;
}

export function LoadingSpinner({ fullPage = false, text = 'Cargando...' }: Props) {
  if (fullPage) {
    return (
      <div
        className="d-flex flex-column align-items-center justify-content-center"
        style={{ minHeight: '60vh' }}
        role="status"
        aria-label={text}
      >
        <div
          className="spinner-border mb-3"
          style={{ width: '2.5rem', height: '2.5rem', color: '#FF0026' }}
        />
        <p className="text-muted small mb-0">{text}</p>
      </div>
    );
  }
  return (
    <span className="spinner-border spinner-border-sm" role="status" aria-label={text} />
  );
}
