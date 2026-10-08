import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { BrandLogoComponent } from '../../shared/ui/components/brand-logo.component';
import { AuthApi, rutaInicial } from '../../features/auth/model/apiAuth';
import { AuthStore } from '../../entities/user/model/authStore';
import { navigationState } from '../../shared/lib/navigationState';
import {
  PASSWORD_MIN_CHAR_TYPES,
  PASSWORD_MIN_LENGTH,
  contarTiposCaracter,
} from '../../shared/config/constants';

interface EstadoRuta {
  username?: string;
  diasRestantesGracia?: number;
}

const BARRA = String.fromCharCode(47);

// AP-0038: cambio autonomo de una contrasena vencida dentro de la ventana de gracia.
// Pagina publica (sin sesion): el usuario llega tras un login con estado 409.
@Component({
  selector: 'app-cambio-contrasena-vencida-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, BrandLogoComponent],
  template: `
    <div
      class="d-flex flex-column align-items-center justify-content-center min-vh-100 px-3"
      style="background: #F4F5FA"
    >
      <div style="width: 100%; max-width: 460px">
        <div class="text-center mb-3">
          <app-brand-logo [height]="32" />
        </div>
        <div class="bg-white rounded-4 shadow-sm p-4 p-md-5">
          <h4 class="fw-bold mb-1" style="color: #100941">Tu contraseña venció</h4>
          <p class="text-muted mb-4" style="font-size: 0.875rem">
            Puedes actualizarla de forma autónoma durante el periodo de gracia.
            @if (diasGracia !== undefined) {
              Te quedan {{ diasGracia }} día(s).
            }
          </p>

          @if (error()) {
            <div class="alert alert-danger py-2 px-3" style="font-size: 0.875rem">
              <i class="bi bi-exclamation-circle me-2"></i>
              {{ error() }}
            </div>
          }

          <form (submit)="handleSubmit($event)" novalidate>
            <div class="mb-3">
              <label class="form-label" for="cv-username">Usuario</label>
              <input id="cv-username" class="form-control" type="text" [value]="username()"
                (input)="username.set($any($event.target).value)" placeholder="Tu usuario" required
                [disabled]="loading()" />
            </div>

            <div class="mb-3">
              <label class="form-label" for="cv-actual">Contraseña actual (vencida)</label>
              <input id="cv-actual" class="form-control" [type]="tipo()" [value]="passwordActual()"
                (input)="passwordActual.set($any($event.target).value)" autocomplete="current-password"
                placeholder="Tu contraseña actual" required [disabled]="loading()" />
            </div>

            <div class="mb-3">
              <label class="form-label" for="cv-nueva">Nueva contraseña</label>
              <div class="input-group">
                <input id="cv-nueva" class="form-control" [type]="tipo()" [value]="nuevaPassword()"
                  (input)="nuevaPassword.set($any($event.target).value)"
                  [placeholder]="'Mínimo ' + minLength + ' caracteres'" [attr.minlength]="minLength" required
                  [disabled]="loading()" />
                <button class="btn btn-outline-secondary" type="button" (click)="mostrar.set(!mostrar())"
                  tabindex="-1" [attr.aria-label]="mostrar() ? 'Ocultar contraseñas' : 'Mostrar contraseñas'">
                  <i class="bi" [class]="mostrar() ? 'bi-eye-slash' : 'bi-eye'"></i>
                </button>
              </div>
            </div>

            <div class="mb-4">
              <label class="form-label" for="cv-confirmar">Confirmar nueva contraseña</label>
              <input id="cv-confirmar" class="form-control" [type]="tipo()" [value]="confirmarPassword()"
                (input)="confirmarPassword.set($any($event.target).value)" placeholder="Repite la nueva contraseña"
                [attr.minlength]="minLength" required [disabled]="loading()" />
            </div>

            <button
              type="submit"
              class="btn btn-primary w-100 py-2"
              [disabled]="loading() || !username() || !passwordActual() || !nuevaPassword() || !confirmarPassword()"
            >
              @if (loading()) {
                <span class="spinner-border spinner-border-sm me-2"></span>
                Actualizando…
              } @else {
                <i class="bi bi-shield-lock me-2"></i>
                Cambiar contraseña e ingresar
              }
            </button>
          </form>
        </div>
        <div class="text-center mt-3">
          <a [routerLink]="rutaLogin" class="text-decoration-none text-muted" style="font-size: 0.85rem">
            <i class="bi bi-arrow-left me-1"></i>
            Volver al inicio de sesión
          </a>
        </div>
      </div>
    </div>
  `,
})
export class CambioContrasenaVencidaPageComponent {
  private readonly router = inject(Router);
  private readonly auth = inject(AuthStore);
  private readonly authApi = inject(AuthApi);
  private readonly estado = navigationState<EstadoRuta>();

  protected readonly minLength = PASSWORD_MIN_LENGTH;
  protected readonly rutaLogin = BARRA + 'login';
  protected readonly diasGracia: number | undefined =
    typeof this.estado.diasRestantesGracia === 'number' ? this.estado.diasRestantesGracia : undefined;

  protected readonly username = signal<string>(this.estado.username ?? '');
  protected readonly passwordActual = signal<string>('');
  protected readonly nuevaPassword = signal<string>('');
  protected readonly confirmarPassword = signal<string>('');
  protected readonly mostrar = signal<boolean>(false);
  protected readonly loading = signal<boolean>(false);
  protected readonly error = signal<string | null>(null);

  protected tipo(): string {
    return this.mostrar() ? 'text' : 'password';
  }

  protected async handleSubmit(e: Event): Promise<void> {
    e.preventDefault();
    this.error.set(null);
    const nueva: string = this.nuevaPassword();

    if (nueva.length < PASSWORD_MIN_LENGTH) {
      this.error.set(`La nueva contraseña debe tener al menos ${PASSWORD_MIN_LENGTH} caracteres`);
      return;
    }
    if (contarTiposCaracter(nueva) < PASSWORD_MIN_CHAR_TYPES) {
      this.error.set(
        `La contraseña debe contener al menos ${PASSWORD_MIN_CHAR_TYPES} de 4 tipos: ` +
          'minúscula, mayúscula, dígito o carácter especial',
      );
      return;
    }
    if (nueva !== this.confirmarPassword()) {
      this.error.set('Las contraseñas no coinciden');
      return;
    }

    this.loading.set(true);
    try {
      await this.authApi.cambiarPasswordExpirada({
        username: this.username(),
        password_actual: this.passwordActual(),
        nueva_password: nueva,
        confirmar_password: this.confirmarPassword(),
      });
      const user = await this.authApi.getMe();
      this.auth.setAuth(user);
      const destino: string = rutaInicial(user, BARRA + 'dashboard');
      void this.router.navigateByUrl(destino, { replaceUrl: true });
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'No se pudo cambiar la contraseña';
      this.error.set(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      this.loading.set(false);
    }
  }
}
