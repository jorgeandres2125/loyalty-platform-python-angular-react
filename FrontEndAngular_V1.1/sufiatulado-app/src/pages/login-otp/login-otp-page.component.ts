import { AutofocusDirective } from '../../shared/ui/directives/autofocus.directive';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { BrandLogoComponent } from '../../shared/ui/components/brand-logo.component';
import { AuthApi, rutaInicial } from '../../features/auth/model/apiAuth';
import { AuthStore } from '../../entities/user/model/authStore';
import { navigationState } from '../../shared/lib/navigationState';
import type { OtpDesafio } from '../../entities/user/model/types';

interface EstadoRuta {
  desafio?: OtpDesafio;
}

// AP-0012: segundo paso del login. El usuario ingresa el codigo OTP de un
// solo uso recibido por correo. Pagina publica: se llega tras un login 202.
@Component({
  selector: 'app-login-otp-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [AutofocusDirective, RouterLink, BrandLogoComponent],
  template: `
    <div
      class="d-flex flex-column align-items-center justify-content-center min-vh-100 px-3"
      style="background: #F4F5FA"
    >
      <div style="width: 100%; max-width: 440px">
        <div class="text-center mb-3">
          <app-brand-logo [height]="32" />
        </div>
        <div class="bg-white rounded-4 shadow-sm p-4 p-md-5">
          <h4 class="fw-bold mb-1" style="color: #100941">Verificacion en dos pasos</h4>
          <p class="text-muted mb-4" style="font-size: 0.875rem">
            Ingresa el codigo de acceso de un solo uso que enviamos a tu correo.
          </p>

          @if (!desafio) {
            <div class="alert alert-warning py-2 px-3" style="font-size: 0.875rem">
              <i class="bi bi-exclamation-triangle me-2"></i>
              No hay un desafio activo. Inicia sesion de nuevo para recibir un codigo.
            </div>
          }

          @if (error()) {
            <div class="alert alert-danger py-2 px-3" style="font-size: 0.875rem">
              <i class="bi bi-exclamation-circle me-2"></i>
              {{ error() }}
            </div>
          }

          @if (desafio) {
            <form (submit)="handleSubmit($event)" novalidate>
              @if (desafio.emailEnmascarado) {
                <p class="text-muted mb-3" style="font-size: 0.85rem">
                  <i class="bi bi-envelope me-1"></i>
                  Codigo enviado a <strong>{{ desafio.emailEnmascarado }}</strong>
                </p>
              }
              <div class="mb-4">
                <label class="form-label" for="otp-codigo">Codigo de acceso</label>
                <input
                  id="otp-codigo"
                  class="form-control"
                  type="text"
                  inputmode="numeric"
                  autocomplete="one-time-code"
                  maxlength="6"
                  [value]="codigo()"
                  (input)="manejarCodigo($event)"
                  placeholder="6 digitos"
                  appAutofocus
                  required
                  [disabled]="loading()"
                />
              </div>
              <button
                type="submit"
                class="btn btn-primary w-100 py-2"
                [disabled]="loading() || codigo().length !== 6"
              >
                @if (loading()) {
                  <span class="spinner-border spinner-border-sm me-2"></span>
                  Verificando...
                } @else {
                  <i class="bi bi-shield-check me-2"></i>
                  Verificar e ingresar
                }
              </button>
            </form>
          }
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
export class LoginOtpPageComponent {
  private readonly router = inject(Router);
  private readonly auth = inject(AuthStore);
  private readonly authApi = inject(AuthApi);

  protected readonly desafio: OtpDesafio | undefined = navigationState<EstadoRuta>().desafio;

  protected readonly codigo = signal<string>('');
  protected readonly loading = signal<boolean>(false);
  protected readonly error = signal<string | null>(null);

  protected async handleSubmit(evento: Event): Promise<void> {
    evento.preventDefault();
    this.error.set(null);
    const desafio = this.desafio;
    if (!desafio) {
      return;
    }
    const codigo: string = this.codigo();
    if (codigo.length !== 6) {
      this.error.set('El codigo debe tener 6 digitos.');
      return;
    }
    this.loading.set(true);
    try {
      await this.authApi.completarLoginOtp({ desafio_id: desafio.desafioId, codigo });
      const user = await this.authApi.getMe();
      this.auth.setAuth(user);
      const destino: string = rutaInicial(user, '/dashboard');
      void this.router.navigateByUrl(destino, { replaceUrl: true });
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'No se pudo verificar el codigo. Intenta de nuevo.';
      this.error.set(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      this.loading.set(false);
    }
  }

  protected manejarCodigo(evento: Event): void {
    const input = evento.target as HTMLInputElement;
    const soloDigitos: string = [...input.value]
      .filter((c) => c >= '0' && c <= '9')
      .join('')
      .slice(0, 6);
    this.codigo.set(soloDigitos);
    input.value = soloDigitos;
  }
}
