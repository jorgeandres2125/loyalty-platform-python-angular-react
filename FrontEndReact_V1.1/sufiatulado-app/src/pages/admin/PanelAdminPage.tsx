import { useNavigate } from 'react-router-dom';
import { Card, Button } from 'react-bootstrap';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { useAuthStore } from '../../entities/user/model/authStore';
import { ROLES } from '../../shared/config/constants';

interface SectionCard {
  icon: string;
  color: string;
  title: string;
  description: string;
  items: string[];
  buttonLabel: string;
  buttonIcon: string;
  route: string;
  adminOnly: boolean;
}

const SECTIONS: SectionCard[] = [
  {
    icon: 'bi-database-fill-gear',
    color: '#1565C0',
    title: 'Administración de catálogos maestros del sistema',
    description: 'Gestiona los catálogos de referencia utilizados en los registros y perfiles de comisionistas.',
    items: [],
    buttonLabel: 'Gestionar Catálogos',
    buttonIcon: 'bi-arrow-right-circle',
    route: '/admin/catalogos',
    adminOnly: true,
  },
  {
    icon: 'bi-person-fill-gear',
    color: '#37474F',
    title: 'Cuenta',
    description: 'Administra tu información de acceso al sistema.',
    items: [],
    buttonLabel: 'Gestionar Cuenta',
    buttonIcon: 'bi-arrow-right-circle',
    route: '/configuraciones',
    adminOnly: false,

  },
  {
    icon: 'bi-person-fill-gear',
    color: '#6A1B9A',
    title: 'Gestión de cuentas de usuario',
    description: 'Habilita o deshabilita el acceso de las cuentas de usuario del sistema.',
    items: [],
    buttonLabel: 'Gestionar Cuentas',
    buttonIcon: 'bi-arrow-right-circle',
    route: '/admin/usuarios',
    adminOnly: true,
  },
  {
    icon: 'bi-shield-lock-fill',
    color: '#B71C1C',
    title: 'Autorizaciones de usuarios',
    description: 'Parametriza los permisos de cada rol sobre los módulos y administra qué usuarios pertenecen a cada rol.',
    items: [],
    buttonLabel: 'Gestionar Autorizaciones',
    buttonIcon: 'bi-arrow-right-circle',
    route: '/admin/autorizaciones',
    adminOnly: true,
  },
];

export function PanelAdminPage() {
  const navigate = useNavigate();
  const { hasRole } = useAuthStore();
  const esAdmin: boolean = hasRole(ROLES.ADMIN);

  const visibles: SectionCard[] = SECTIONS.filter((s) => !s.adminOnly || esAdmin);

  return (
    <div>
      <PageHeader
        title="Panel de Control"
        subtitle="Accesos rápidos para la gestión del sistema"
        icon="bi-grid-3x3-gap-fill"
      />

      <div className="row g-4">
        {visibles.map((section) => (
          <div key={section.route} className="col-12 col-md-6">
            <Card className="h-100 border-0 shadow-sm">
              <Card.Body className="p-4 d-flex flex-column">
                <div className="d-flex align-items-center gap-3 mb-3">
                  <div
                    className="rounded-3 d-flex align-items-center justify-content-center flex-shrink-0"
                    style={{ width: 56, height: 56, background: section.color, color: '#fff', fontSize: '1.6rem' }}
                  >
                    <i className={`bi ${section.icon}`} />
                  </div>
                  <h5 className="mb-0 fw-bold lh-sm">{section.title}</h5>
                </div>

                <p className="text-muted mb-3" style={{ fontSize: '0.9rem' }}>
                  {section.description}
                </p>

                <ul className="list-unstyled mb-4 flex-grow-1">
                  {section.items.map((item) => (
                    <li key={item} className="d-flex align-items-center gap-2 mb-1" style={{ fontSize: '0.875rem' }}>
                      <i className="bi bi-check-circle-fill text-success" style={{ fontSize: '0.75rem' }} />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  variant="primary"
                  className="w-100 d-flex align-items-center justify-content-center gap-2"
                  onClick={() => navigate(section.route)}
                >
                  <i className={`bi ${section.buttonIcon}`} />
                  {section.buttonLabel}
                </Button>
              </Card.Body>
            </Card>
          </div>
        ))}
      </div>
    </div>
  );
}
