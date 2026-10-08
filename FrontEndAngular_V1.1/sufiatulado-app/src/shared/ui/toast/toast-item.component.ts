import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  computed,
  effect,
  inject,
  input,
  output,
  signal,
} from '@angular/core';
import type { ToastVariant } from './toast.service';

// Variantes de fondo oscuro: el texto y el boton de cierre van en claro.
const VARIANTES_OSCURAS: ReadonlySet<ToastVariant> = new Set([
  'success',
  'danger',
  'primary',
  'secondary',
  'dark',
  'info',
]);

/** Toast individual de Bootstrap (equivalente a `ToastItem`). */
@Component({
  selector: 'app-toast-item',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { class: 'd-block' },
  template: `
    <div
      class="toast fade"
      [class.show]="visible()"
      [class]="'bg-' + bgColor()"
      role="alert"
      [attr.aria-live]="ariaLive()"
      aria-atomic="true"
    >
      <div class="toast-header">
        @if (icon()) {
          <span class="me-2 fs-5 lh-1" aria-hidden="true">
            @if (icon()!.startsWith('bi-')) {
              <i class="bi" [class]="icon()"></i>
            } @else {
              {{ icon() }}
            }
          </span>
        }
        <strong class="me-auto">{{ title() }}</strong>
        <button
          type="button"
          class="btn-close"
          [class.btn-close-white]="oscuro()"
          aria-label="Close"
          (click)="cerrar()"
        ></button>
      </div>
      @if (message() || detail()) {
        <div class="toast-body" [class.text-white]="oscuro()">
          @if (message()) {
            <div>{{ message() }}</div>
          }
          @if (detail()) {
            <div class="small mt-1 opacity-75">{{ detail() }}</div>
          }
        </div>
      }
    </div>
  `,
})
export class ToastItemComponent {
  readonly title = input<string>('Notificacion');
  readonly message = input<string>('');
  readonly detail = input<string | undefined>(undefined);
  readonly bgColor = input<ToastVariant>('primary');
  readonly icon = input<string | undefined>(undefined);
  readonly delay = input<number>(10000);
  readonly autohide = input<boolean>(true);

  readonly closed = output<void>();

  protected readonly visible = signal<boolean>(false);
  protected readonly oscuro = computed<boolean>(() => VARIANTES_OSCURAS.has(this.bgColor()));
  // Error y advertencia se anuncian de forma asertiva a lectores de pantalla;
  // el resto, de forma cortes (polite). Accesibilidad basica (a11y).
  protected readonly ariaLive = computed<'assertive' | 'polite'>(() =>
    this.bgColor() === 'danger' || this.bgColor() === 'warning' ? 'assertive' : 'polite',
  );

  private timer: ReturnType<typeof setTimeout> | undefined;

  constructor() {
    // Entrada con fade (como react-bootstrap) y autocierre tras `delay`.
    requestAnimationFrame(() => this.visible.set(true));
    effect((onCleanup) => {
      if (!this.autohide()) return;
      const id = setTimeout(() => this.cerrar(), this.delay());
      onCleanup(() => clearTimeout(id));
    });
    inject(DestroyRef).onDestroy(() => clearTimeout(this.timer));
  }

  protected cerrar(): void {
    this.visible.set(false);
    clearTimeout(this.timer);
    // Espera la transicion de salida antes de retirar el toast del stack.
    this.timer = setTimeout(() => this.closed.emit(), 150);
  }
}
