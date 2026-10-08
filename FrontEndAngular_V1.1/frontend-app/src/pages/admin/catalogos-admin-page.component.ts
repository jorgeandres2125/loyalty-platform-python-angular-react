import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';

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
  { code: 'AFP', title: 'AFP', description: 'Fondos de pensiones', icon: 'bi-piggy-bank-fill', color: '#2E7D32', route: '/admin/afp', enabled: true },
  { code: 'ARL', title: 'ARL', description: 'Administradoras de Riesgos Laborales', icon: 'bi-shield-fill-plus', color: '#C62828', route: '/admin/arl', enabled: true },
  { code: 'EPS', title: 'EPS', description: 'Entidades Promotoras de Salud', icon: 'bi-heart-pulse-fill', color: '#1565C0', route: '/admin/eps', enabled: true },
  { code: 'BANCOS', title: 'Bancos', description: 'Entidades financieras para cuentas bancarias', icon: 'bi-bank2', color: '#6A1B9A', route: '/admin/bancos', enabled: true },
  { code: 'DEPARTAMENTOS', title: 'Departamentos', description: 'Departamentos geográficos de Colombia', icon: 'bi-map-fill', color: '#EF6C00', route: '/admin/departamentos', enabled: true },
  { code: 'CIUDADES', title: 'Ciudades', description: 'Ciudades por departamento', icon: 'bi-geo-alt-fill', color: '#F9A825', route: '/admin/ciudades', enabled: true },
  { code: 'COMISIONISTAS_PROGRAMA', title: 'Programas', description: 'Movilidad / Consumo y Servicios (solo edición de nombre)', icon: 'bi-bookmark-star-fill', color: '#00838F', route: '/admin/programas', enabled: true },
  { code: 'COMISIONISTAS_SUBPROGRAMA', title: 'Sub-programas', description: 'Sub-programas por programa', icon: 'bi-bookmarks-fill', color: '#00695C', route: '/admin/subprogramas', enabled: true },
  { code: 'TAXONOMIA_PROFESION', title: 'Profesiones', description: 'Catálogo de profesiones del registro', icon: 'bi-briefcase-fill', color: '#4527A0', route: '/admin/profesiones', enabled: true },
];

@Component({
  selector: 'app-catalogos-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent],
  template: `
    <div>
      <app-page-header
        title="Catálogos Maestros"
        [subtitle]="catalogos.length + ' catálogos disponibles'"
        icon="bi-database-fill-gear"
        backTo="/admin/dashboard"
      />

      <div class="row g-3">
        @for (cat of catalogos; track cat.code) {
          <div class="col-12 col-sm-6 col-lg-4 col-xl-3">
            <div
              class="card h-100 border-0 shadow-sm panel-admin-card"
              [class.panel-admin-card--disabled]="!cat.enabled"
              [style.cursor]="cat.enabled ? 'pointer' : 'not-allowed'"
              [style.opacity]="cat.enabled ? 1 : 0.65"
              (click)="cat.enabled && ir(cat.route)"
              [attr.role]="cat.enabled ? 'button' : null"
              [attr.tabindex]="cat.enabled ? 0 : -1"
              (keydown)="onKey($event, cat)"
            >
              <div class="card-body d-flex flex-column">
                <div class="d-flex align-items-start justify-content-between mb-3">
                  <div
                    class="rounded-3 d-flex align-items-center justify-content-center"
                    style="width: 52px; height: 52px; color: #fff; font-size: 1.5rem"
                    [style.background]="cat.color"
                  >
                    <i class="bi" [class]="cat.icon"></i>
                  </div>
                  @if (!cat.enabled) {
                    <span class="badge bg-secondary text-uppercase">Próximamente</span>
                  }
                </div>
                <div class="card-title h5 mb-1 fw-bold">{{ cat.title }}</div>
                <p class="card-text text-muted small mb-3 flex-grow-1">{{ cat.description }}</p>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-primary"
                  [disabled]="!cat.enabled"
                  (click)="$event.stopPropagation(); cat.enabled && ir(cat.route)"
                >
                  <i class="bi bi-gear-fill me-2"></i>
                  Administrar
                </button>
              </div>
            </div>
          </div>
        }
      </div>
    </div>
  `,
})
export class CatalogosAdminPageComponent {
  private readonly router = inject(Router);
  protected readonly catalogos = CATALOGOS;

  protected ir(route: string): void {
    void this.router.navigateByUrl(route);
  }

  protected onKey(e: KeyboardEvent, cat: CatalogoCard): void {
    if (cat.enabled && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      this.ir(cat.route);
    }
  }
}
