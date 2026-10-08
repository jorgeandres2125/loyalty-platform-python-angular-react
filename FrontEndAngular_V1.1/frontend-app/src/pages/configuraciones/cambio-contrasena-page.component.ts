import { ChangeDetectionStrategy, Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { ApiClient } from '../../shared/api/client';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { formTimeout } from '../../shared/lib/formTimeout';
import {
  AUTH_FORM_TIMEOUT_MS,
  PASSWORD_MIN_CHAR_TYPES,
  PASSWORD_MIN_LENGTH,
  contarTiposCaracter,
} from '../../shared/config/constants';

@Component({
  selector: 'app-cambio-contrasena-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent],
  template: `
    <div class="cambio-contrasena-page">
      <app-page-header title="Cambiar Contraseña" icon="bi-lock-fill" backTo="/configuraciones" />

      <div class="cambio-contrasena-page__card">
        @if (exito()) {
          <div class="alert alert-success text-center mb-0">
            <i class="bi bi-check-circle-fill me-2"></i>
            Contraseña actualizada correctamente. Redirigiendo…
          </div>
        } @else {
          <form (submit)="handleSubmit($event)" novalidate>
            @if (error()) {
              <div class="alert alert-danger alert-dismissible" role="alert">
                <i class="bi bi-exclamation-circle me-2"></i>
                {{ error() }}
                <button type="button" class="btn-close" aria-label="Close" (click)="error.set(null)"></button>
              </div>
            }

            @if (expirado()) {
              <div class="alert alert-warning" role="alert">
                <i class="bi bi-clock-history me-2"></i>
                Por seguridad se limpiaron los datos tras 1 minuto sin enviarlos. Ingrésalos de nuevo.
              </div>
            }

            <div class="mb-3">
              <label class="form-label cambio-contrasena-page__label" for="passwordActual">
                Contraseña Actual
              </label>
              <div class="input-group">
                <input
                  id="passwordActual"
                  class="form-control"
                  [type]="showActual() ? 'text' : 'password'"
                  [value]="passwordActual()"
                  (input)="passwordActual.set($any($event.target).value); expirado.set(false)"
                  placeholder="Tu contraseña actual"
                  autocomplete="current-password"
                  required
                  [disabled]="loading()"
                />
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  (click)="showActual.set(!showActual())"
                  tabindex="-1"
                  [attr.aria-label]="showActual() ? 'Ocultar contraseña actual' : 'Mostrar contraseña actual'"
                >
                  <i class="bi" [class]="showActual() ? 'bi-eye-slash' : 'bi-eye'"></i>
                </button>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label cambio-contrasena-page__label" for="nuevaPassword">
                Nueva Contraseña
              </label>
              <div class="input-group">
                <input
                  id="nuevaPassword"
                  class="form-control"
                  [type]="showNueva() ? 'text' : 'password'"
                  [value]="nuevaPassword()"
                  (input)="nuevaPassword.set($any($event.target).value); expirado.set(false)"
                  [placeholder]="'Mínimo ' + minLength + ' caracteres'"
                  required
                  [attr.minlength]="minLength"
                  [disabled]="loading()"
                />
                <button type="button" class="btn btn-outline-secondary" (click)="showNueva.set(!showNueva())" tabindex="-1">
                  <i class="bi" [class]="showNueva() ? 'bi-eye-slash' : 'bi-eye'"></i>
                </button>
              </div>
            </div>

            <div class="mb-4">
              <label class="form-label cambio-contrasena-page__label" for="confirmarPassword">
                Confirmar Nueva Contraseña
              </label>
              <div class="input-group">
                <input
                  id="confirmarPassword"
                  class="form-control"
                  [type]="showConfirmar() ? 'text' : 'password'"
                  [value]="confirmarPassword()"
                  (input)="confirmarPassword.set($any($event.target).value); expirado.set(false)"
                  placeholder="Repite la nueva contraseña"
                  required
                  [attr.minlength]="minLength"
                  [disabled]="loading()"
                />
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  (click)="showConfirmar.set(!showConfirmar())"
                  tabindex="-1"
                >
                  <i class="bi" [class]="showConfirmar() ? 'bi-eye-slash' : 'bi-eye'"></i>
                </button>
              </div>
            </div>

            <button
              type="submit"
              class="btn btn-primary w-100 cambio-contrasena-page__submit"
              [disabled]="loading() || !passwordActual() || !nuevaPassword() || !confirmarPassword()"
            >
              @if (loading()) {
                <span class="spinner-border spinner-border-sm me-2"></span>
                Actualizando…
              } @else {
                <i class="bi bi-check-lg me-2"></i>
                Actualizar Contraseña
              }
            </button>
          </form>
        }
      </div>
    </div>
  `,
})
export class CambioContrasenaPageComponent {
  private readonly router = inject(Router);
  private readonly api = inject(ApiClient);

  protected readonly minLength = PASSWORD_MIN_LENGTH;

  protected readonly passwordActual = signal<string>('');
  protected readonly nuevaPassword = signal<string>('');
  protected readonly confirmarPassword = signal<string>('');
  protected readonly showActual = signal<boolean>(false);
  protected readonly showNueva = signal<boolean>(false);
  protected readonly showConfirmar = signal<boolean>(false);
  protected readonly loading = signal<boolean>(false);
  protected readonly error = signal<string | null>(null);
  protected readonly exito = signal<boolean>(false);
  protected readonly expirado = signal<boolean>(false);

  private redireccion: ReturnType<typeof setTimeout> | undefined;

  constructor() {
    inject(DestroyRef).onDestroy(() => clearTimeout(this.redireccion));

    // AP-0018: límite absoluto de 1 min desde la primera interacción. Vencido el
    // plazo sin enviar, se borran las contraseñas tecleadas.
    const hayInteraccion = computed<boolean>(
      () =>
        this.passwordActual().length > 0 ||
        this.nuevaPassword().length > 0 ||
        this.confirmarPassword().length > 0,
    );
    formTimeout({
      delayMs: AUTH_FORM_TIMEOUT_MS,
      active: computed<boolean>(() => hayInteraccion() && !this.loading() && !this.exito()),
      onTimeout: () => {
        this.passwordActual.set('');
        this.nuevaPassword.set('');
        this.confirmarPassword.set('');
        this.showActual.set(false);
        this.showNueva.set(false);
        this.showConfirmar.set(false);
        this.error.set(null);
        this.expirado.set(true);
      },
    });
  }

  protected async handleSubmit(e: Event): Promise<void> {
    e.preventDefault();
    this.error.set(null);
    const nueva: string = this.nuevaPassword();

    // AP-0044: política de longitud mínima para usuarios finales.
    if (nueva.length < PASSWORD_MIN_LENGTH) {
      this.error.set(`La nueva contraseña debe tener al menos ${PASSWORD_MIN_LENGTH} caracteres`);
      return;
    }

    // AP-0051: complejidad — al menos 3 de los 4 tipos de carácter.
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
      await this.api.patch('/auth/password', {
        password_actual: this.passwordActual(),
        nueva_password: nueva,
        confirmar_password: this.confirmarPassword(),
      });
      this.exito.set(true);
      this.redireccion = setTimeout(() => void this.router.navigateByUrl('/configuraciones'), 2000);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Error al cambiar la contraseña';
      this.error.set(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      this.loading.set(false);
    }
  }
}
