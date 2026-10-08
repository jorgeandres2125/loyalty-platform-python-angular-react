import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../shared/api/client';
import { useAuthStore } from '../../entities/user/model/authStore';
import { LoadingSpinner } from '../../shared/ui/components/LoadingSpinner';
import { ROLES } from '../../shared/config/constants';
import { MiDashboardComisionista } from './MiDashboardComisionista';


interface ProgramaStats {
  total: number;
  activos: number;
  incompletos: number;
  con_incentivos: number;
  nuevos_mes: number;
}

interface DashboardStats {
  movilidad: ProgramaStats;
  consumo: ProgramaStats;
}

interface StatCardProps {
  icon: string;
  label: string;
  value: number | string;
  color: string;
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  return (
    <div className="stat-card">
      <div
        className="stat-card__icon"
        style={{ '--s-color': color, '--s-bg': `${color}18` } as React.CSSProperties}
      >
        <i className={`bi ${icon}`} />
      </div>
      <div>
        <div className="stat-card__value">{value}</div>
        <div className="stat-card__label">{label}</div>
      </div>
    </div>
  );
}

interface ProgramaSectionProps {
  label: string;
  icon: string;
  accent: string;
  stats: ProgramaStats;
}

function ProgramaSection({ label, icon, accent, stats }: ProgramaSectionProps) {
  return (
    <div className="mb-4">
      <div className="d-flex align-items-center gap-2 mb-3">
        <div
          className="rounded-2 d-flex align-items-center justify-content-center flex-shrink-0"
          style={{ width: 32, height: 32, background: accent }}
        >
          <i className={`bi ${icon} text-white`} style={{ fontSize: '0.9rem' }} />
        </div>
        <h6 className="mb-0 fw-semibold">{label}</h6>
      </div>
      <div className="row g-3 row-cols-2 row-cols-sm-3 row-cols-lg-5">
        <div className="col">
          <StatCard
            icon="bi-people-fill"
            label="Total registrados"
            value={stats.total.toLocaleString('es-CO')}
            color="#6B7280"
          />
        </div>
        <div className="col">
          <StatCard
            icon="bi-person-check-fill"
            label="Activos"
            value={stats.activos.toLocaleString('es-CO')}
            color="#10B981"
          />
        </div>
        <div className="col">
          <StatCard
            icon="bi-hourglass-split"
            label="Incompletos"
            value={stats.incompletos.toLocaleString('es-CO')}
            color="#F59E0B"
          />
        </div>
        <div className="col">
          <StatCard
            icon="bi-stars"
            label="Con incentivos"
            value={stats.con_incentivos.toLocaleString('es-CO')}
            color="#EAB308"
          />
        </div>
        <div className="col">
          <StatCard
            icon="bi-person-plus-fill"
            label="Nuevos este mes"
            value={stats.nuevos_mes.toLocaleString('es-CO')}
            color="#3B82F6"
          />
        </div>
      </div>
    </div>
  );
}

export function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const isAdmin = useAuthStore((s) =>
    s.hasRole(ROLES.ADMIN) || s.hasRole(ROLES.WEBMASTER) || s.hasRole(ROLES.EJECUTIVO)
  );
  const isComisionistaMovilidad = useAuthStore((s) => s.hasRole(ROLES.COMISIONISTA));
  const isComisionistaConsumo = useAuthStore((s) => s.hasRole(ROLES.COMISIONISTA_CONSUMO));
  const esComisionista: boolean = isComisionistaMovilidad || isComisionistaConsumo;

  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const { data } = await apiClient.get<DashboardStats>('/dashboard/stats');
      return data;
    },
    enabled: isAdmin && !esComisionista,
    staleTime: 60_000,
  });

  // Vista personalizada para comisionistas (precede a la vista administrativa)
  if (isComisionistaMovilidad) {
    return <MiDashboardComisionista perfilRoute="/perfil-movilidad" />;
  }
  if (isComisionistaConsumo) {
    return <MiDashboardComisionista perfilRoute="/perfil-consumo" />;
  }

  return (
    <div className="dashboard">
      {/* Bienvenida */}
      <div className="mb-4">
        <h2 className="dashboard__welcome-title">
          Bienvenido{user ? `, ${user.username}` : ''}
        </h2>
        <p className="text-muted mb-0 small">
          {new Date().toLocaleDateString('es-CO', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </p>
      </div>

      {/* Estadísticas por programa */}
      {isAdmin && (
        <div className="mb-4">
          {isLoading ? (
            <div className="d-flex align-items-center gap-2 py-3 text-muted">
              <LoadingSpinner />
              <span className="small">Cargando estadísticas…</span>
            </div>
          ) : stats ? (
            <>
              <ProgramaSection
                label="Movilidad (Vehículos)"
                icon="bi-car-front-fill"
                accent="#2563EB"
                stats={stats.movilidad}
              />
              <ProgramaSection
                label="Consumo y Servicios"
                icon="bi-bag-fill"
                accent="#16A34A"
                stats={stats.consumo}
              />
            </>
          ) : null}
        </div>
      )}

    </div>
  );
}
