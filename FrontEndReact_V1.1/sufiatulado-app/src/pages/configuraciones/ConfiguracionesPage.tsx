import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../shared/ui/components/PageHeader';

interface SettingItem {
  icon: string;
  color: string;
  title: string;
  subtitle: string;
  to: string;
  disabled?: boolean;
}

const ITEMS: SettingItem[] = [
  {
    icon: 'bi-lock-fill',
    color: '#FF0026',
    title: 'Cambiar Contraseña',
    subtitle: 'Actualiza tus credenciales de acceso',
    to: '/configuraciones/cambio_contrasena',
  },
  {
    icon: 'bi-laptop',
    color: '#0D6EFD',
    title: 'Mis Sesiones',
    subtitle: 'Consulta y cierra tus sesiones activas',
    to: '/configuraciones/sesiones',
  },
];

export function ConfiguracionesPage() {
  const navigate = useNavigate();

  return (
    <div className="configuraciones-page">
      <PageHeader title="Cuenta" icon="bi-person-fill-gear" backTo="/admin/dashboard" />

      <div className="configuraciones-page__list">
        {ITEMS.map((item) => (
          <button
            key={item.to}
            className="configuraciones-page__item"
            onClick={() => navigate(item.to)}
            disabled={item.disabled}
          >
            <span
              className="configuraciones-page__item-icon"
              style={{ background: item.color }}
            >
              <i className={`bi ${item.icon}`} />
            </span>
            <span className="configuraciones-page__item-body">
              <span className="configuraciones-page__item-title">{item.title}</span>
              <span className="configuraciones-page__item-subtitle">{item.subtitle}</span>
            </span>
            <i className="bi bi-chevron-right configuraciones-page__item-arrow" />
          </button>
        ))}
      </div>
    </div>
  );
}
