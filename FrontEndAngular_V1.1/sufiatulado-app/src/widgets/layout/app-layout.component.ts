import { ChangeDetectionStrategy, Component, computed, effect, inject, signal } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { TopbarComponent } from './topbar.component';
import { IdleWarningModalComponent } from '../../shared/ui/idle-warning-modal.component';
import { AuthApi } from '../../features/auth/model/apiAuth';
import { AuthStore } from '../../entities/user/model/authStore';
import { passwordExpiryToast } from '../../features/password-expiry/model/passwordExpiryToast';
import { idleTimeout } from '../../shared/lib/idleTimeout';
import { IDLE_WARNING_MS, limiteInactividadMs } from '../../shared/lib/idlePolicy';
import { SesionLocal } from '../../shared/lib/limpiarSesionLocal';

@Component({
  selector: 'app-layout',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterOutlet, TopbarComponent, IdleWarningModalComponent],
  template: `
    <div class="app-shell">
      <app-topbar />
      <main class="app-main">
        <router-outlet />
      </main>
      <app-idle-warning-modal
        [show]="avisoVisible()"
        [segundosRestantes]="segundosRestantes()"
        (continuar)="continuarSesion()"
        (cerrar)="cerrarSesion()"
      />
    </div>
  `,
})
export class AppLayoutComponent {
  private readonly auth = inject(AuthStore);
  private readonly authApi = inject(AuthApi);
  private readonly sesionLocal = inject(SesionLocal);
  private readonly router = inject(Router);

  protected readonly avisoVisible = signal<boolean>(false);
  protected readonly segundosRestantes = signal<number>(60);

  private readonly idleMs = computed<number>(() => limiteInactividadMs(this.auth.roles()));

  constructor() {
    this.authApi
      .getMe()
      .then((u) => this.auth.setAuth(u))
      .catch(() => undefined);

    passwordExpiryToast();

    // Igual que ProtectedRoute en React: si la sesión local desaparece (cierre por
    // inactividad, expiración, logout en otra parte) se vuelve a /login de inmediato.
    effect(() => {
      if (!this.auth.isAuthenticated()) {
        void this.router.navigateByUrl('/login', { replaceUrl: true });
      }
    });

    // Cuenta regresiva del aviso de inactividad.
    effect((onCleanup) => {
      if (!this.avisoVisible()) return;
      this.segundosRestantes.set(60);
      const id = setInterval(() => {
        this.segundosRestantes.update((s) => (s > 0 ? s - 1 : 0));
      }, 1000);
      onCleanup(() => clearInterval(id));
    });

    // AP-0132: expiracion proactiva. El backend expone session_expires_at (no secreto) en
    // auth/me; al alcanzarlo se descartan los datos locales sin leer el token (HttpOnly).
    const sessionExpiresAt = computed<string | null>(() => this.auth.user()?.session_expires_at ?? null);
    effect((onCleanup) => {
      const expira = sessionExpiresAt();
      if (!expira) return;
      const restanteMs: number = new Date(expira).getTime() - Date.now();
      if (restanteMs <= 0) {
        this.sesionLocal.limpiar();
        return;
      }
      const id = setTimeout(() => this.sesionLocal.limpiar(), restanteMs);
      onCleanup(() => clearTimeout(id));
    });

    idleTimeout({
      idleMs: this.idleMs,
      warningMs: IDLE_WARNING_MS,
      active: this.auth.isAuthenticated,
      onWarning: () => this.avisoVisible.set(true),
      onTimeout: () => this.cerrarSesion(),
      onActivity: () => {
        this.authApi.refresh().catch(() => undefined);
      },
    });
  }

  protected cerrarSesion(): void {
    this.avisoVisible.set(false);
    // AP-0132: al cerrar por inactividad se descartan tambien los datos locales.
    this.authApi
      .logout()
      .catch(() => undefined)
      .finally(() => this.sesionLocal.limpiar());
  }

  protected continuarSesion(): void {
    this.avisoVisible.set(false);
    this.authApi.refresh().catch(() => this.cerrarSesion());
  }
}
