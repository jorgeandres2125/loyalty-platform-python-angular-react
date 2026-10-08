import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { Router } from '@angular/router';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { AuthStore } from '../../entities/user/model/authStore';
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
    description:
      'Parametriza los permisos de cada rol sobre los módulos y administra qué usuarios pertenecen a cada rol.',
    items: [],
    buttonLabel: 'Gestionar Autorizaciones',
    buttonIcon: 'bi-arrow-right-circle',
    route: '/admin/autorizaciones',
    adminOnly: true,
  },
];

@Component({
  selector: 'app-panel-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent],
  template: `
    <div>
      <app-page-header
        title="Panel de Control"
        subtitle="Accesos rápidos para la gestión del sistema"
        icon="bi-grid-3x3-gap-fill"
      />

      <div class="row g-4">
        @for (section of visibles(); track section.route) {
          <div class="col-12 col-md-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body p-4 d-flex flex-column">
                <div class="d-flex align-items-center gap-3 mb-3">
                  <div
                    class="rounded-3 d-flex align-items-center justify-content-center flex-shrink-0"
                    style="width: 56px; height: 56px; color: #fff; font-size: 1.6rem"
                    [style.background]="section.color"
                  >
                    <i class="bi" [class]="section.icon"></i>
                  </div>
                  <h5 class="mb-0 fw-bold lh-sm">{{ section.title }}</h5>
                </div>

                <p class="text-muted mb-3" style="font-size: 0.9rem">{{ section.description }}</p>

                <ul class="list-unstyled mb-4 flex-grow-1">
                  @for (item of section.items; track item) {
                    <li class="d-flex align-items-center gap-2 mb-1" style="font-size: 0.875rem">
                      <i class="bi bi-check-circle-fill text-success" style="font-size: 0.75rem"></i>
                      <span>{{ item }}</span>
                    </li>
                  }
                </ul>

                <button
                  type="button"
                  class="btn btn-primary w-100 d-flex align-items-center justify-content-center gap-2"
                  (click)="ir(section.route)"
                >
                  <i class="bi" [class]="section.buttonIcon"></i>
                  {{ section.buttonLabel }}
                </button>
              </div>
            </div>
          </div>
        }
      </div>
    </div>
  `,
})
export class PanelAdminPageComponent {
  private readonly router = inject(Router);
  private readonly auth = inject(AuthStore);

  protected readonly visibles = computed<SectionCard[]>(() => {
    this.auth.user();
    const esAdmin: boolean = this.auth.hasRole(ROLES.ADMIN);
    return SECTIONS.filter((s) => !s.adminOnly || esAdmin);
  });

  protected ir(route: string): void {
    void this.router.navigateByUrl(route);
  }
}
