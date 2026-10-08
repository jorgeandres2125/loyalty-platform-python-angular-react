import {
  ChangeDetectionStrategy,
  Component,
  DOCUMENT,
  DestroyRef,
  computed,
  effect,
  inject,
  input,
  output,
} from '@angular/core';

/**
 * Modal de Bootstrap 5 controlado por signals (sustituye a `react-bootstrap/Modal`).
 * El contenido se proyecta dentro de `.modal-content`; usar las clases estándar
 * `modal-header` / `modal-body` / `modal-footer`.
 *
 *   <app-modal [show]="abierto()" (hide)="abierto.set(false)" centered>
 *     <div class="modal-header">…</div>
 *     <div class="modal-body">…</div>
 *   </app-modal>
 */
@Component({
  selector: 'app-modal',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { '(document:keydown.escape)': 'onEscape()' },
  template: `
    @if (show()) {
      <div class="modal-backdrop fade show"></div>
      <div
        class="modal fade show d-block"
        tabindex="-1"
        role="dialog"
        aria-modal="true"
        (mousedown)="onBackdrop($event)"
      >
        <div class="modal-dialog" [class]="dialogClass()">
          <div class="modal-content">
            <ng-content />
          </div>
        </div>
      </div>
    }
  `,
})
export class ModalComponent {
  readonly show = input<boolean>(false);
  readonly size = input<'sm' | 'lg' | 'xl' | undefined>(undefined);
  readonly centered = input<boolean>(false);
  readonly scrollable = input<boolean>(false);
  /** `static`: el clic en el fondo no cierra el modal. */
  readonly backdrop = input<boolean | 'static'>(true);
  readonly keyboard = input<boolean>(true);
  readonly dialogClassName = input<string>('');

  readonly hide = output<void>();

  protected readonly dialogClass = computed<string>(() => {
    const clases: string[] = ['modal-dialog'];
    if (this.size()) clases.push(`modal-${this.size()}`);
    if (this.centered()) clases.push('modal-dialog-centered');
    if (this.scrollable()) clases.push('modal-dialog-scrollable');
    if (this.dialogClassName()) clases.push(this.dialogClassName());
    return clases.join(' ');
  });

  constructor() {
    const doc = inject(DOCUMENT);
    // Bloquea el scroll del body mientras el modal está abierto (como Bootstrap).
    effect((onCleanup) => {
      if (!this.show()) return;
      doc.body.classList.add('modal-open');
      doc.body.style.overflow = 'hidden';
      onCleanup(() => {
        doc.body.classList.remove('modal-open');
        doc.body.style.overflow = '';
      });
    });
    inject(DestroyRef).onDestroy(() => {
      doc.body.classList.remove('modal-open');
      doc.body.style.overflow = '';
    });
  }

  protected onEscape(): void {
    if (this.show() && this.keyboard()) this.hide.emit();
  }

  protected onBackdrop(evento: MouseEvent): void {
    if (this.backdrop() === 'static') return;
    if (evento.target === evento.currentTarget) this.hide.emit();
  }
}
