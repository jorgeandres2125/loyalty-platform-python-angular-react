import { useNavigate } from 'react-router-dom';

interface Props {
  title: string;
  subtitle?: string;
  icon?: string;
  actions?: React.ReactNode;
  backTo?: string;
}

export function PageHeader({ title, subtitle, icon, actions, backTo }: Props) {
  const navigate = useNavigate();

  return (
    <div className="page-header d-flex align-items-start justify-content-between gap-3 flex-wrap">
      <div className="d-flex align-items-center gap-2">
        {backTo && (
          <button
            className="page-header__back"
            onClick={() => navigate(backTo)}
            aria-label="Volver"
          >
            <i className="bi bi-arrow-left" />
          </button>
        )}
        <div>
          <h2 className="d-flex align-items-center gap-2">
            {icon && <i className={`bi ${icon} text-sufi-red`} style={{ fontSize: '1.5rem' }} />}
            {title}
          </h2>
          {subtitle && <p className="page-subtitle">{subtitle}</p>}
        </div>
      </div>
      {actions && <div className="d-flex gap-2 flex-wrap">{actions}</div>}
    </div>
  );
}
