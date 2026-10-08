interface Props {
  icon?: string;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon = 'bi-inbox', title, description, action }: Props) {
  return (
    <div className="text-center py-5 px-4">
      <i className={`bi ${icon}`} style={{ fontSize: '3rem', color: '#B2BFCC' }} />
      <h6 className="mt-3 fw-semibold" style={{ color: '#333241' }}>{title}</h6>
      {description && <p className="text-muted small mb-3">{description}</p>}
      {action}
    </div>
  );
}
