import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthStore } from '../../entities/user/model/authStore';
import { AuthApi } from '../../features/auth/model/apiAuth';
import { ROLES } from '../../shared/config/constants';
import { navigateWithTransition } from '../../shared/lib/viewTransition';
import { SesionLocal } from '../../shared/lib/limpiarSesionLocal';
import { BrandLogoComponent } from '../../shared/ui/components/brand-logo.component';

interface NavItem {
  to: string;
  icon: string;
  label: string;
}

const FALLBACK_ICON = 'bi-grid' as const;

const PANEL_ROLES: ReadonlySet<string> = new Set([
  ROLES.ADMIN,
  ROLES.WEBMASTER,
  ROLES.COMISIONISTA,
  ROLES.COMISIONISTA_CONSUMO,
  ROLES.ASESOR_CONSUMO,
  ROLES.ASESOR_LOGISTICO,
  ROLES.ASESOR_COMERCIAL,
  ROLES.ASESOR_CALLCENTER,
]);

@Component({
  selector: 'app-topbar',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, RouterLinkActive, BrandLogoComponent],
  template: `
    <header class="topbar">
      <!-- ── Main bar ── -->
      <div class="topbar__bar">
        <!-- Logo -->
        <a routerLink="/dashboard" class="topbar__logo">
          <app-brand-logo [height]="36" />
        </a>

        <!-- Desktop nav — visible from xl up -->
        <nav class="topbar__nav d-none d-xl-flex" aria-label="Navegación principal">
          @for (item of navItems(); track item.to) {
            <a
              [routerLink]="item.to"
              routerLinkActive="active"
              [routerLinkActiveOptions]="{ exact: item.to === '/dashboard' }"
              class="topbar__nav-link"
            >
              <i class="bi" [class]="item.icon" aria-hidden="true"></i>
              {{ item.label }}
            </a>
          }
        </nav>

        <!-- Right side -->
        <div class="topbar__actions">
          @if (auth.user(); as user) {
            <span class="topbar__user-email d-none d-xxl-inline">{{ user.email }}</span>
            <button class="topbar__logout-btn" (click)="handleLogout()" title="Cerrar sesión">
              <div class="topbar__avatar">{{ user.username.charAt(0).toUpperCase() }}</div>
              <span class="d-none d-sm-inline">{{ user.username }}</span>
              <i class="bi bi-box-arrow-right"></i>
            </button>
          } @else {
            <a routerLink="/login" class="topbar__login-link">
              <i class="bi bi-box-arrow-in-right"></i>
              Ingresar
            </a>
          }

          <!-- Hamburger — visible below xl -->
          <button
            class="topbar__hamburger d-xl-none"
            (click)="menuOpen.set(!menuOpen())"
            [attr.aria-label]="menuOpen() ? 'Cerrar menú' : 'Abrir menú'"
            [attr.aria-expanded]="menuOpen()"
          >
            <i class="bi" [class]="menuOpen() ? 'bi-x-lg' : 'bi-list'"></i>
          </button>
        </div>
      </div>

      <!-- ── Mobile / tablet dropdown ── -->
      @if (menuOpen()) {
        <nav class="topbar__mobile-nav" aria-label="Menú móvil">
          <div class="topbar__mobile-grid">
            @for (item of navItems(); track item.to) {
              <a
                [routerLink]="item.to"
                routerLinkActive="active"
                [routerLinkActiveOptions]="{ exact: item.to === '/dashboard' }"
                (click)="menuOpen.set(false)"
                class="topbar__mobile-link"
              >
                <i class="bi" [class]="item.icon"></i>
                {{ item.label }}
              </a>
            }
          </div>

          @if (auth.user()) {
            <button class="topbar__mobile-logout" (click)="menuOpen.set(false); handleLogout()">
              <i class="bi bi-box-arrow-right"></i>
              Cerrar sesión
            </button>
          }
        </nav>
      }
    </header>
  `,
})
export class TopbarComponent {
  protected readonly auth = inject(AuthStore);
  private readonly authApi = inject(AuthApi);
  private readonly sesionLocal = inject(SesionLocal);
  private readonly router = inject(Router);

  protected readonly menuOpen = signal<boolean>(false);

  protected readonly navItems = computed<NavItem[]>(() => {
    const dbItems: NavItem[] = this.auth
      .modulosVisibles()
      .filter((modulo) => modulo.ruta && modulo.module_code !== 'PANEL_ADMIN')
      .map((modulo) => ({
        to: modulo.ruta as string,
        icon: modulo.icono ?? FALLBACK_ICON,
        label: modulo.nombre,
      }));

    const tienePanel: boolean = this.auth.user()?.roles.some((r) => PANEL_ROLES.has(r)) ?? false;

    if (tienePanel) {
      dbItems.push({
        to: '/admin/dashboard',
        icon: 'bi-grid-3x3-gap-fill',
        label: 'Panel de Control',
      });
    }

    return dbItems;
  });

  protected handleLogout(): void {
    // Borra la cookie de sesión en el backend (fire-and-forget) y limpia el estado.
    void this.authApi.logout().catch(() => undefined);
    this.sesionLocal.limpiar();
    navigateWithTransition(() => void this.router.navigateByUrl('/login'));
  }
}
