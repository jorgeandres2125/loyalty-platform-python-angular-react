import { useNavigate } from 'react-router-dom';
import { Badge, Card } from 'react-bootstrap';
import { PageHeader } from '../../shared/ui/components/PageHeader';

interface CatalogoCard {
  code: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  route: string;
  enabled: boolean;
}

const CATALOGOS: CatalogoCard[] = [
  {
    code: 'AFP',
    title: 'AFP',
    description: 'Fondos de pensiones',
    icon: 'bi-piggy-bank-fill',
    color: '#2E7D32',
    route: '/admin/afp',
    enabled: true,
  },
  {
    code: 'ARL',
    title: 'ARL',
    description: 'Administradoras de Riesgos Laborales',
    icon: 'bi-shield-fill-plus',
    color: '#C62828',
    route: '/admin/arl',
    enabled: true,
  },
  {
    code: 'EPS',
    title: 'EPS',
    description: 'Entidades Promotoras de Salud',
    icon: 'bi-heart-pulse-fill',
    color: '#1565C0',
    route: '/admin/eps',
    enabled: true,
  },
  {
    code: 'BANCOS',
    title: 'Bancos',
    description: 'Entidades financieras para cuentas bancarias',
    icon: 'bi-bank2',
    color: '#6A1B9A',
    route: '/admin/bancos',
    enabled: true,
  },
  {
    code: 'DEPARTAMENTOS',
    title: 'Departamentos',
    description: 'Departamentos geográficos de Colombia',
    icon: 'bi-map-fill',
    color: '#EF6C00',
    route: '/admin/departamentos',
    enabled: true,
  },
  {
    code: 'CIUDADES',
    title: 'Ciudades',
    description: 'Ciudades por departamento',
    icon: 'bi-geo-alt-fill',
    color: '#F9A825',
    route: '/admin/ciudades',
    enabled: true,
  },
  {
    code: 'COMISIONISTAS_PROGRAMA',
    title: 'Programas',
    description: 'Movilidad / Consumo y Servicios (solo edición de nombre)',
    icon: 'bi-bookmark-star-fill',
    color: '#00838F',
    route: '/admin/programas',
    enabled: true,
  },
  {
    code: 'COMISIONISTAS_SUBPROGRAMA',
    title: 'Sub-programas',
    description: 'Sub-programas por programa',
    icon: 'bi-bookmarks-fill',
    color: '#00695C',
    route: '/admin/subprogramas',
    enabled: true,
  },
  {
    code: 'TAXONOMIA_PROFESION',
    title: 'Profesiones',
    description: 'Catálogo de profesiones del registro',
    icon: 'bi-briefcase-fill',
    color: '#4527A0',
    route: '/admin/profesiones',
    enabled: true,
  },
];

export function CatalogosAdminPage() {
  const navigate = useNavigate();

  return (
    <div>
      <PageHeader
        title="Catálogos Maestros"
        subtitle={`${CATALOGOS.length} catálogos disponibles`}
        icon="bi-database-fill-gear"
        backTo="/admin/dashboard"
      />

      <div className="row g-3">
        {CATALOGOS.map((cat) => (
          <div key={cat.code} className="col-12 col-sm-6 col-lg-4 col-xl-3">
            <Card
              className={`h-100 border-0 shadow-sm panel-admin-card${cat.enabled ? '' : ' panel-admin-card--disabled'}`}
              style={{ cursor: cat.enabled ? 'pointer' : 'not-allowed', opacity: cat.enabled ? 1 : 0.65 }}
              onClick={() => cat.enabled && navigate(cat.route)}
              role={cat.enabled ? 'button' : undefined}
              tabIndex={cat.enabled ? 0 : -1}
              onKeyDown={(e) => {
                if (cat.enabled && (e.key === 'Enter' || e.key === ' ')) {
                  e.preventDefault();
                  navigate(cat.route);
                }
              }}
            >
              <Card.Body className="d-flex flex-column">
                <div className="d-flex align-items-start justify-content-between mb-3">
                  <div
                    className="rounded-3 d-flex align-items-center justify-content-center"
                    style={{ width: 52, height: 52, background: cat.color, color: '#fff', fontSize: '1.5rem' }}
                  >
                    <i className={`bi ${cat.icon}`} />
                  </div>
                  {!cat.enabled && (
                    <Badge bg="secondary" className="text-uppercase">Próximamente</Badge>
                  )}
                </div>
                <Card.Title className="mb-1 fw-bold">{cat.title}</Card.Title>
                <Card.Text className="text-muted small mb-3 flex-grow-1">
                  {cat.description}
                </Card.Text>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-primary"
                  disabled={!cat.enabled}
                  onClick={(e) => { e.stopPropagation(); if (cat.enabled) navigate(cat.route); }}
                >
                  <i className="bi bi-gear-fill me-2" />
                  Administrar
                </button>
              </Card.Body>
            </Card>
          </div>
        ))}
      </div>
    </div>
  );
}
