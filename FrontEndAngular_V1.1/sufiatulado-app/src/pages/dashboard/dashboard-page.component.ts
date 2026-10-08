import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../shared/api/client';
import { AuthStore } from '../../entities/user/model/authStore';
import { LoadingSpinnerComponent } from '../../shared/ui/components/loading-spinner.component';
import { ROLES } from '../../shared/config/constants';
import { MiDashboardComisionistaComponent } from './mi-dashboard-comisionista.component';
import { ProgramaSectionComponent, type ProgramaStats } from './programa-section.component';

interface DashboardStats {
  movilidad: ProgramaStats;
  consumo: ProgramaStats;
}

@Component({
  selector: 'app-dashboard-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [LoadingSpinnerComponent, MiDashboardComisionistaComponent, ProgramaSectionComponent],
  template: `
    <!-- Vista personalizada para comisionistas (precede a la vista administrativa) -->
    @if (isComisionistaMovilidad()) {
      <app-mi-dashboard-comisionista perfilRoute="/perfil-movilidad" />
    } @else if (isComisionistaConsumo()) {
      <app-mi-dashboard-comisionista perfilRoute="/perfil-consumo" />
    } @else {
      <div class="dashboard">
        <!-- Bienvenida -->
        <div class="mb-4">
          <h2 class="dashboard__welcome-title">
            Bienvenido{{ auth.user() ? ', ' + auth.user()!.username : '' }}
          </h2>
          <p class="text-muted mb-0 small">{{ fechaHoy }}</p>
        </div>

        <!-- Estadísticas por programa -->
        @if (isAdmin()) {
          <div class="mb-4">
            @if (stats.isLoading()) {
              <div class="d-flex align-items-center gap-2 py-3 text-muted">
                <app-loading-spinner />
                <span class="small">Cargando estadísticas…</span>
              </div>
            } @else if (stats.data(); as data) {
              <app-programa-section
                label="Movilidad (Vehículos)"
                icon="bi-car-front-fill"
                accent="#2563EB"
                [stats]="data.movilidad"
              />
              <app-programa-section
                label="Consumo y Servicios"
                icon="bi-bag-fill"
                accent="#16A34A"
                [stats]="data.consumo"
              />
            }
          </div>
        }
      </div>
    }
  `,
})
export class DashboardPageComponent {
  protected readonly auth = inject(AuthStore);
  private readonly api = inject(ApiClient);

  protected readonly isAdmin = computed<boolean>(() => {
    this.auth.user();
    return (
      this.auth.hasRole(ROLES.ADMIN) ||
      this.auth.hasRole(ROLES.WEBMASTER) ||
      this.auth.hasRole(ROLES.EJECUTIVO)
    );
  });
  protected readonly isComisionistaMovilidad = computed<boolean>(() => {
    this.auth.user();
    return this.auth.hasRole(ROLES.COMISIONISTA);
  });
  protected readonly isComisionistaConsumo = computed<boolean>(() => {
    this.auth.user();
    return this.auth.hasRole(ROLES.COMISIONISTA_CONSUMO);
  });

  protected readonly fechaHoy: string = new Date().toLocaleDateString('es-CO', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  protected readonly stats = injectQuery<DashboardStats>(() => ({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const { data } = await this.api.get<DashboardStats>('/dashboard/stats');
      return data;
    },
    enabled: this.isAdmin() && !(this.isComisionistaMovilidad() || this.isComisionistaConsumo()),
    staleTime: 60_000,
  }));
}
