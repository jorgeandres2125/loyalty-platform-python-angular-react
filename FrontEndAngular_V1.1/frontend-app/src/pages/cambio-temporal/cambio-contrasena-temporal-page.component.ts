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
  expiraIso?: string;
}

// AP-0046: cambio obligatorio de la contrasena temporal tras su primer uso.
// Pagina publica (sin sesion): el usuario llega tras un login con estado 409.
@Component({
  selector: 'app-cambio-contrasena-temporal-page',
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
          <h4 class="fw-bold mb-1" style="color: #100941">Define tu contrasena personal</h4>
          <p class="text-muted mb-4" style="font-size: 0.875rem">
            Ingresaste con una contrasena temporal de un solo uso. Para continuar,
            crea ahora tu contrasena personal.
          </p>

          @if (error()) {
            <div class="alert alert-danger py-2 px-3" style="font-size: 0.875rem">
              <i class="bi bi-exclamation-circle me-2"></i>
              {{ error() }}
            </div>
          }

          <form (submit)="handleSubmit($event)" novalidate>
            <div class="mb-3">
              <label class="form-label" for="ct-username">Usuario</label>
              <input id="ct-username" class="form-control" type="text" [value]="username()"
                (input)="username.set($any($event.target).value)" placeholder="Tu usuario" required
                [disabled]="loading()" />
            </div>

            <div class="mb-3">
              <label class="form-label" for="ct-temporal">Contrasena temporal</label>
              <input id="ct-temporal" class="form-control" [type]="tipo()" [value]="passwordTemporal()"
                (input)="passwordTemporal.set($any($event.target).value)" autocomplete="one-time-code"
                placeholder="La contrasena temporal que recibiste" required [disabled]="loading()" />
            </div>

            <div class="mb-3">
              <label class="form-label" for="ct-nueva">Nueva contrasena</label>
              <div class="input-group">
                <input id="ct-nueva" class="form-control" [type]="tipo()" [value]="nuevaPassword()"
                  (input)="nuevaPassword.set($any($event.target).value)"
                  [placeholder]="'Minimo ' + minLength + ' caracteres'" [attr.minlength]="minLength" required
                  [disabled]="loading()" />
                <button class="btn btn-outline-secondary" type="button" (click)="mostrar.set(!mostrar())"
                  tabindex="-1" [attr.aria-label]="mostrar() ? 'Ocultar contrasenas' : 'Mostrar contrasenas'">
                  <i class="bi" [class]="mostrar() ? 'bi-eye-slash' : 'bi-eye'"></i>
                </button>
              </div>
            </div>

            <div class="mb-4">
              <label class="form-label" for="ct-confirmar">Confirmar nueva contrasena</label>
              <input id="ct-confirmar" class="form-control" [type]="tipo()" [value]="confirmarPassword()"
                (input)="confirmarPassword.set($any($event.target).value)" placeholder="Repite la nueva contrasena"
                [attr.minlength]="minLength" required [disabled]="loading()" />
            </div>

            <button
              type="submit"
              class="btn btn-primary w-100 py-2"
              [disabled]="loading() || !username() || !passwordTemporal() || !nuevaPassword() || !confirmarPassword()"
            >
              @if (loading()) {
                <span class="spinner-border spinner-border-sm me-2"></span>
                Guardando…
              } @else {
                <i class="bi bi-shield-lock me-2"></i>
                Crear contrasena e ingresar
              }
            </button>
          </form>
        </div>
        <div class="text-center mt-3">
          <a routerLink="/login" class="text-decoration-none text-muted" style="font-size: 0.85rem">
            <i class="bi bi-arrow-left me-1"></i>
            Volver al inicio de sesion
          </a>
        </div>
      </div>
    </div>
  `,
})
export class CambioContrasenaTemporalPageComponent {
  private readonly router = inject(Router);
  private readonly auth = inject(AuthStore);
  private readonly authApi = inject(AuthApi);
  private readonly estado = navigationState<EstadoRuta>();

  protected readonly minLength = PASSWORD_MIN_LENGTH;

  protected readonly username = signal<string>(this.estado.username ?? '');
  protected readonly passwordTemporal = signal<string>('');
  protected readonly nuevaPassword = signal<string>('');
  protected readonly confirmarPassword = signal<string>('');
  protected readonly mostrar = signal<boolean>(false);
  protected readonly loading = signal<boolean>(false);
  protected readonly error = signal<string | null>(null);

  protected tipo(): string {
    return this.mostrar() ? 'text' : 'password';
  }

  protected async handleSubmit(evento: Event): Promise<void> {
    evento.preventDefault();
    this.error.set(null);
    const nueva: string = this.nuevaPassword();

    if (nueva.length < PASSWORD_MIN_LENGTH) {
      this.error.set(`La nueva contrasena debe tener al menos ${PASSWORD_MIN_LENGTH} caracteres`);
      return;
    }
    if (contarTiposCaracter(nueva) < PASSWORD_MIN_CHAR_TYPES) {
      this.error.set(
        `La contrasena debe contener al menos ${PASSWORD_MIN_CHAR_TYPES} de 4 tipos: ` +
          'minuscula, mayuscula, digito o caracter especial',
      );
      return;
    }
    if (nueva !== this.confirmarPassword()) {
      this.error.set('Las contrasenas no coinciden');
      return;
    }

    this.loading.set(true);
    try {
      await this.authApi.cambiarPasswordTemporal({
        username: this.username(),
        password_temporal: this.passwordTemporal(),
        nueva_password: nueva,
        confirmar_password: this.confirmarPassword(),
      });
      const user = await this.authApi.getMe();
      this.auth.setAuth(user);
      const destino: string = rutaInicial(user, '/dashboard');
      void this.router.navigateByUrl(destino, { replaceUrl: true });
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'No se pudo cambiar la contrasena';
      this.error.set(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      this.loading.set(false);
    }
  }
}
