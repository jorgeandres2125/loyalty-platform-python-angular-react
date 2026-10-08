import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { getProblemMessage } from '../../../shared/api/problemDetails';
import { injectConfirmarCodigo, injectSolicitarCodigo } from '../model/verificacionEmail';
import { formTimeout } from '../../../shared/lib/formTimeout';
import { AUTH_FORM_TIMEOUT_MS } from '../../../shared/config/constants';
import { AutofocusDirective } from '../../../shared/ui/directives/autofocus.directive';

type Paso = 'solicitar' | 'confirmar' | 'verificado';

const TIPOS_DOCUMENTO: ReadonlyArray<{ value: string; label: string }> = [
  { value: 'C.C.', label: 'Cédula de ciudadanía' },
  { value: 'C.E.', label: 'Cédula de extranjería' },
  { value: 'TI', label: 'Tarjeta de identidad' },
  { value: 'PA', label: 'Pasaporte' },
  { value: 'NIT', label: 'NIT' },
];

const MENSAJE_NEUTRO =
  'Si los datos corresponden a un registro con correo, te enviamos un código de 8 dígitos. Revisa tu bandeja de entrada (y la carpeta de spam).';

@Component({
  selector: 'app-verificacion-email-form',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [AutofocusDirective],
  template: `
    @switch (paso()) {
      <!-- ── Paso 3: verificado ── -->
      @case ('verificado') {
        <div class="text-center py-3">
          <div
            class="d-inline-flex align-items-center justify-content-center rounded-circle mb-3"
            style="width: 72px; height: 72px; background: #D1F4E0"
          >
            <i class="bi bi-check-lg" style="font-size: 2.5rem; color: #0F7B4E"></i>
          </div>
          <h4 class="fw-bold mb-2" style="color: #100941">Correo verificado</h4>
          <p class="text-muted mb-0" style="font-size: 0.9rem">
            Confirmamos que el correo te pertenece. Ya puedes cerrar esta ventana.
          </p>
        </div>
      }

      <!-- ── Paso 2: confirmar código ── -->
      @case ('confirmar') {
        <form (submit)="handleConfirmar($event)" novalidate style="width: 100%">
          <h4 class="fw-bold mb-1" style="color: #100941">Ingresa el código</h4>
          <div class="alert alert-info py-2 px-3 mb-3" style="font-size: 0.85rem">
            <i class="bi bi-envelope-check me-2"></i>
            {{ emailEnmascarado() ? 'Enviamos un código de 8 dígitos a ' + emailEnmascarado() + '.' : mensajeNeutro }}
          </div>

          @if (confirmar.isError()) {
            <div class="alert alert-danger py-2 px-3" style="font-size: 0.85rem">
              <i class="bi bi-exclamation-circle me-2"></i>
              {{ mensajeErrorConfirmar() }}
            </div>
          }

          <div class="mb-3">
            <label class="form-label" for="ve-codigo">Código de verificación</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0">
                <i class="bi bi-shield-lock text-muted"></i>
              </span>
              <input
                id="ve-codigo"
                type="text"
                inputmode="numeric"
                autocomplete="one-time-code"
                placeholder="8 dígitos"
                class="form-control border-start-0"
                style="letter-spacing: 0.3rem; font-weight: 600"
                maxlength="8"
                [value]="codigo()"
                (input)="onCodigo($event)"
                required
                appAutofocus
              />
            </div>
          </div>

          <button
            type="submit"
            class="btn btn-primary w-100 py-2 mb-2"
            [disabled]="confirmar.isPending() || codigo().length !== 8"
          >
            @if (confirmar.isPending()) {
              <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Verificando...
            } @else {
              <i class="bi bi-check2-circle me-2"></i>
              Verificar correo
            }
          </button>

          <div class="d-flex justify-content-between">
            <button type="button" class="btn btn-link px-0 text-decoration-none" style="font-size: 0.85rem"
              (click)="paso.set('solicitar')">
              <i class="bi bi-arrow-left me-1"></i>
              Cambiar documento
            </button>
            <button type="button" class="btn btn-link px-0 text-decoration-none" style="font-size: 0.85rem"
              (click)="handleReenviar()" [disabled]="solicitar.isPending()">
              {{ solicitar.isPending() ? 'Reenviando...' : 'Reenviar código' }}
            </button>
          </div>
        </form>
      }

      <!-- ── Paso 1: solicitar código ── -->
      @default {
        <form (submit)="handleSolicitar($event)" novalidate style="width: 100%">
          <h4 class="fw-bold mb-1" style="color: #100941">Verifica tu correo</h4>
          <p class="text-muted mb-4" style="font-size: 0.875rem">
            Te enviaremos un código al correo registrado para confirmar que te pertenece.
          </p>

          @if (expirado()) {
            <div class="alert alert-warning py-2 px-3 mb-3" style="font-size: 0.85rem">
              <i class="bi bi-clock-history me-2"></i>
              Por seguridad se limpiaron tus datos tras 1 minuto sin enviarlos. Ingrésalos de nuevo.
            </div>
          }

          <div class="mb-3">
            <label class="form-label" for="ve-tipo">Tipo de documento</label>
            <select id="ve-tipo" class="form-select" [value]="tipoDocumento()"
              (change)="tipoDocumento.set($any($event.target).value)">
              @for (t of tipos; track t.value) {
                <option [value]="t.value" [selected]="t.value === tipoDocumento()">{{ t.label }}</option>
              }
            </select>
          </div>

          <div class="mb-4">
            <label class="form-label" for="ve-numero">Número de documento</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0">
                <i class="bi bi-person-vcard text-muted"></i>
              </span>
              <input
                id="ve-numero"
                type="text"
                inputmode="numeric"
                placeholder="Solo números"
                class="form-control border-start-0"
                [value]="numeroDocumento()"
                (input)="onNumero($event)"
                required
                appAutofocus
              />
            </div>
          </div>

          <button
            type="submit"
            class="btn btn-primary w-100 py-2"
            [disabled]="solicitar.isPending() || numeroDocumento().length < 3"
          >
            @if (solicitar.isPending()) {
              <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Enviando código...
            } @else {
              <i class="bi bi-envelope-arrow-up me-2"></i>
              Enviar código
            }
          </button>
        </form>
      }
    }
  `,
})
export class VerificacionEmailFormComponent {
  protected readonly tipos = TIPOS_DOCUMENTO;
  protected readonly mensajeNeutro = MENSAJE_NEUTRO;

  protected readonly solicitar = injectSolicitarCodigo();
  protected readonly confirmar = injectConfirmarCodigo();

  protected readonly paso = signal<Paso>('solicitar');
  protected readonly tipoDocumento = signal<string>('C.C.');
  protected readonly numeroDocumento = signal<string>('');
  protected readonly codigo = signal<string>('');
  protected readonly emailEnmascarado = signal<string | null>(null);
  protected readonly expirado = signal<boolean>(false);

  protected readonly mensajeErrorConfirmar = computed<string>(() =>
    getProblemMessage(this.confirmar.error(), 'No se pudo validar el código.'),
  );

  constructor() {
    // El enlace del correo trae ?doc=&tipo= → aterrizamos directo en el paso de
    // ingresar el código, con el documento ya resuelto (solo falta teclear el código).
    const query = inject(ActivatedRoute).snapshot.queryParamMap;
    const docParam: string = (query.get('doc') ?? '').replace(/\D/g, '').slice(0, 20);
    const tipoParam: string | null = query.get('tipo');
    const tipoInicial: string = TIPOS_DOCUMENTO.some((t) => t.value === tipoParam)
      ? (tipoParam as string)
      : 'C.C.';
    this.paso.set(docParam ? 'confirmar' : 'solicitar');
    this.tipoDocumento.set(tipoInicial);
    this.numeroDocumento.set(docParam);

    // AP-0018: límite absoluto de 1 min desde la primera interacción. Vencido el
    // plazo sin enviar, se borran el documento/código tecleados y se vuelve al inicio.
    const hayInteraccion = computed<boolean>(
      () =>
        this.paso() !== 'verificado' &&
        (this.numeroDocumento().length > 0 || this.codigo().length > 0),
    );
    formTimeout({
      delayMs: AUTH_FORM_TIMEOUT_MS,
      active: computed<boolean>(
        () => hayInteraccion() && !this.solicitar.isPending() && !this.confirmar.isPending(),
      ),
      onTimeout: () => {
        this.numeroDocumento.set('');
        this.codigo.set('');
        this.emailEnmascarado.set(null);
        this.confirmar.reset();
        this.paso.set('solicitar');
        this.expirado.set(true);
      },
    });
  }

  protected onCodigo(e: Event): void {
    const input = e.target as HTMLInputElement;
    const valor: string = input.value.replace(/\D/g, '').slice(0, 8);
    this.codigo.set(valor);
    input.value = valor;
  }

  protected onNumero(e: Event): void {
    const input = e.target as HTMLInputElement;
    const valor: string = input.value.replace(/\D/g, '').slice(0, 20);
    this.numeroDocumento.set(valor);
    input.value = valor;
    this.expirado.set(false);
  }

  protected handleSolicitar(e: Event): void {
    e.preventDefault();
    this.confirmar.reset();
    this.solicitar.mutate(
      { tipo_documento: this.tipoDocumento(), numero_documento: this.numeroDocumento() },
      {
        onSuccess: (data) => {
          this.emailEnmascarado.set(data.email_enmascarado);
          this.codigo.set('');
          this.paso.set('confirmar');
        },
      },
    );
  }

  protected handleConfirmar(e: Event): void {
    e.preventDefault();
    this.confirmar.mutate(
      {
        tipo_documento: this.tipoDocumento(),
        numero_documento: this.numeroDocumento(),
        codigo: this.codigo(),
      },
      { onSuccess: () => this.paso.set('verificado') },
    );
  }

  protected handleReenviar(): void {
    this.confirmar.reset();
    this.solicitar.mutate({
      tipo_documento: this.tipoDocumento(),
      numero_documento: this.numeroDocumento(),
    });
  }
}
