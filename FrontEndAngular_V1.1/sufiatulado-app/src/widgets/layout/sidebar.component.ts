import { ChangeDetectionStrategy, Component, computed, inject, input, output } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthStore } from '../../entities/user/model/authStore';
import { AuthApi } from '../../features/auth/model/apiAuth';
import { ROLES } from '../../shared/config/constants';
import { navigateWithTransition } from '../../shared/lib/viewTransition';
import { BrandLogoComponent } from '../../shared/ui/components/brand-logo.component';

interface NavItem {
  to: string;
  icon: string;
  label: string;
  roles: string[];
}

// Rutas heredadas que aun no tienen module_code en el backend; se muestran por rol.
const EXTRA_ITEMS: NavItem[] = [
  { to: '/documentos', icon: 'bi-file-earmark-text', label: 'Documentos', roles: [ROLES.ADMIN, ROLES.WEBMASTER, ROLES.DOCUMENTADOR] },
  { to: '/referencias', icon: 'bi-diagram-3', label: 'Referencias', roles: [ROLES.ADMIN, ROLES.WEBMASTER] },
];

/** Barra lateral (conservada del proyecto React; el layout actual usa la Topbar). */
@Component({
  selector: 'app-sidebar',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, RouterLinkActive, BrandLogoComponent],
  template: `
    @if (isOpen()) {
      <div
        class="d-lg-none position-fixed top-0 start-0 w-100 h-100"
        style="background: rgba(0,0,0,0.4); z-index: 999"
        (click)="closed.emit()"
        aria-hidden="true"
      ></div>
    }
    <aside class="sidebar" [class.open]="isOpen()" aria-label="Navegacion principal">
      <div class="sidebar__logo">
        <app-brand-logo [height]="34" />
      </div>

      <nav class="sidebar__nav">
        <ul class="list-unstyled mb-0">
          @for (item of items(); track item.to) {
            <li>
              <a
                [routerLink]="item.to"
                routerLinkActive="active"
                [routerLinkActiveOptions]="{ exact: item.to === '/dashboard' }"
                class="nav-item-link"
                (click)="closed.emit()"
              >
                <i class="bi nav-icon" [class]="item.icon" aria-hidden="true"></i>
                <span>{{ item.label }}</span>
              </a>
            </li>
          }
        </ul>
      </nav>

      <div class="sidebar__footer">
        @if (auth.user(); as user) {
          <div class="mb-3">
            <div class="d-flex align-items-center gap-2">
              <div
                class="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
                style="width: 32px; height: 32px; background: rgba(255,255,255,0.1); color: #fff; font-size: 0.875rem; font-weight: 600"
              >
                {{ user.username.charAt(0).toUpperCase() }}
              </div>
              <div class="overflow-hidden">
                <div class="text-white fw-semibold text-truncate" style="font-size: 0.8rem">
                  {{ user.username }}
                </div>
                <div style="font-size: 0.7rem; color: rgba(255,255,255,0.5)">
                  {{ user.roles.length ? user.roles[0] : 'usuario' }}
                </div>
              </div>
            </div>
          </div>
        }
        <button
          class="btn btn-sm w-100 text-start d-flex align-items-center gap-2"
          style="color: rgba(255,255,255,0.6); background: transparent; border: none"
          (click)="handleLogout()"
        >
          <i class="bi bi-box-arrow-left"></i>
          Cerrar sesion
        </button>
      </div>
    </aside>
  `,
})
export class SidebarComponent {
  protected readonly auth = inject(AuthStore);
  private readonly authApi = inject(AuthApi);
  private readonly router = inject(Router);

  readonly isOpen = input<boolean>(false);
  readonly closed = output<void>();

  // Menu data-driven: el backend resuelve roles + permisos en `modulos` (puede_ver
  // ya viene filtrado y ordenado por `orden`). SAPIN conserva su compuerta de
  // incentivos (puede_ver por si solo no la modela).
  protected readonly items = computed<NavItem[]>(() => {
    const dynamicItems: NavItem[] = this.auth
      .modulosVisibles()
      .filter((m) => m.ruta !== null && m.ruta !== '')
      .filter((m) => (m.module_code === 'SAPIN' ? this.auth.canAccessSapin() : true))
      .map((m) => ({ to: m.ruta as string, icon: m.icono ?? 'bi-dot', label: m.nombre, roles: [] }));

    const rutasDinamicas: Set<string> = new Set(dynamicItems.map((item) => item.to));
    const extraItems: NavItem[] = EXTRA_ITEMS.filter(
      (item) => !rutasDinamicas.has(item.to) && item.roles.some((rol) => this.auth.hasRole(rol)),
    );
    return [...dynamicItems, ...extraItems];
  });

  protected handleLogout(): void {
    void this.authApi.logout().catch(() => undefined);
    this.auth.logout();
    navigateWithTransition(() => void this.router.navigateByUrl('/login'));
  }
}
