import { AutofocusDirective } from '../../../shared/ui/directives/autofocus.directive';
import { ChangeDetectionStrategy, Component, computed, effect, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { injectLogin } from '../model/login';
import { formTimeout } from '../../../shared/lib/formTimeout';
import { AUTH_FORM_TIMEOUT_MS } from '../../../shared/config/constants';
import { isApiError } from '../../../shared/api/apiError';
import type { OtpDesafio } from '../../../entities/user/model/types';

const LOGIN_ERROR_VISIBLE_MS = 10000;

function mensajeDeError(error: unknown): string {
  const generico = 'Credenciales inválidas. Intenta de nuevo.';
  if (isApiError(error)) {
    const detalle = (error.response?.data as { detail?: unknown } | null)?.detail;
    if (typeof detalle === 'string' && detalle.trim().length > 0) {
      return detalle;
    }
  }
  return generico;
}

@Component({
  selector: 'app-login-form',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [AutofocusDirective, FormsModule, RouterLink],
  template: `
    <form (ngSubmit)="handleSubmit()" novalidate style="width: 100%">
      <h4 class="fw-bold mb-1" style="color: #100941">Iniciar sesión</h4>
      <p class="text-muted mb-4" style="font-size: 0.875rem">Accede a tu plataforma SUFI Contigo</p>

      @if (errorMsg()) {
        <div class="alert alert-danger py-2 px-3" role="alert" style="font-size: 0.875rem">
          <i class="bi bi-exclamation-circle me-2"></i>
          {{ errorMsg() }}
        </div>
      }

      @if (otpDesafio(); as desafio) {
        <div class="alert alert-info py-2 px-3" role="alert" style="font-size: 0.875rem">
          <i class="bi bi-shield-lock me-2"></i>
          {{ desafio.mensaje }}
          @if (desafio.emailEnmascarado) {
            <span class="d-block text-muted mt-1">Codigo enviado a {{ desafio.emailEnmascarado }}</span>
          }
          <div class="mt-2">
            <button class="btn btn-primary btn-sm" type="button" (click)="irAlOtp()">
              <i class="bi bi-key me-1"></i>
              Ingresar codigo de acceso
            </button>
          </div>
        </div>
      }

      @if (expirado()) {
        <div class="alert alert-warning py-2 px-3" role="alert" style="font-size: 0.875rem">
          <i class="bi bi-clock-history me-2"></i>
          Por seguridad se limpiaron tus datos tras 1 minuto sin enviarlos. Ingrésalos de nuevo.
        </div>
      }

      <div class="mb-3">
        <label class="form-label" for="login-username">Usuario</label>
        <div class="input-group">
          <span class="input-group-text bg-light border-end-0">
            <i class="bi bi-person text-muted"></i>
          </span>
          <input
            id="login-username"
            name="username"
            type="text"
            class="form-control border-start-0"
            placeholder="Tu usuario"
            [ngModel]="username()"
            (ngModelChange)="username.set($event); expirado.set(false)"
            required
            appAutofocus
          />
        </div>
      </div>

      <div class="mb-4">
        <label class="form-label" for="login-password">Contraseña</label>
        <div class="input-group">
          <span class="input-group-text bg-light border-end-0">
            <i class="bi bi-lock text-muted"></i>
          </span>
          <input
            id="login-password"
            name="password"
            [type]="showPass() ? 'text' : 'password'"
            class="form-control border-start-0 border-end-0"
            placeholder="Tu contraseña"
            [ngModel]="password()"
            (ngModelChange)="password.set($event); expirado.set(false)"
            required
          />
          <button
            class="btn btn-light border"
            type="button"
            (click)="showPass.set(!showPass())"
            tabindex="-1"
            [attr.aria-label]="showPass() ? 'Ocultar contraseña' : 'Mostrar contraseña'"
          >
            <i class="bi text-muted" [class]="showPass() ? 'bi-eye-slash' : 'bi-eye'"></i>
          </button>
        </div>
      </div>

      <button
        type="submit"
        class="btn btn-primary w-100 py-2"
        [disabled]="login.isPending() || !username() || !password()"
      >
        @if (login.isPending()) {
          <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          Ingresando...
        } @else {
          <i class="bi bi-box-arrow-in-right me-2"></i>
          Ingresar
        }
      </button>

      <div class="text-center mt-3">
        <a routerLink="/verificar-correo" class="text-decoration-none" style="font-size: 0.85rem">
          <i class="bi bi-envelope-check me-1"></i>
          Verificar mi correo electrónico
        </a>
      </div>
    </form>
  `,
})
export class LoginFormComponent {
  private readonly router = inject(Router);

  protected readonly username = signal<string>('');
  protected readonly password = signal<string>('');
  protected readonly showPass = signal<boolean>(false);
  protected readonly expirado = signal<boolean>(false);
  protected readonly errorMsg = signal<string | null>(null);
  protected readonly otpDesafio = signal<OtpDesafio | null>(null);
  protected readonly login = injectLogin();

  constructor() {
    effect((onCleanup) => {
      const error = this.login.error();
      if (!error) return;
      this.errorMsg.set(mensajeDeError(error));
      const id = window.setTimeout(() => this.errorMsg.set(null), LOGIN_ERROR_VISIBLE_MS);
      onCleanup(() => window.clearTimeout(id));
    });

    // AP-0012: cuando el backend exige OTP guardamos el desafio para mostrar
    // el enlace de ingreso del codigo. El mensaje se muestra en el toast.
    effect(() => {
      const data = this.login.data();
      if (data && data.kind === 'otp') {
        this.otpDesafio.set(data.desafio);
        this.errorMsg.set(null);
      }
    });

    // AP-0018: límite absoluto de 1 min desde la primera interacción. Vencido el
    // plazo sin enviar, se borran las credenciales tecleadas.
    const hayInteraccion = computed<boolean>(
      () => this.username().length > 0 || this.password().length > 0,
    );
    formTimeout({
      delayMs: AUTH_FORM_TIMEOUT_MS,
      active: computed<boolean>(() => hayInteraccion() && !this.login.isPending()),
      onTimeout: () => {
        this.username.set('');
        this.password.set('');
        this.showPass.set(false);
        this.expirado.set(true);
      },
    });
  }

  protected handleSubmit(): void {
    this.errorMsg.set(null);
    this.otpDesafio.set(null);
    this.login.mutate({ username: this.username(), password: this.password() });
  }

  protected irAlOtp(): void {
    const desafio = this.otpDesafio();
    if (desafio) {
      void this.router.navigate(['/login/otp'], { state: { desafio } });
    }
  }
}
