import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { ModalComponent } from './modal.component';

export type ConfirmVariant = 'primary' | 'danger' | 'warning' | 'success' | 'info';

/**
 * Modal de confirmación (equivalente a `ConfirmModal`). El mensaje se pasa con
 * `message` (texto) o proyectando contenido: <app-confirm-modal>…</app-confirm-modal>.
 */
@Component({
  selector: 'app-confirm-modal',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ModalComponent],
  template: `
    <app-modal
      [show]="show()"
      [centered]="true"
      [size]="size()"
      [backdrop]="loading() ? 'static' : true"
      [keyboard]="!loading()"
      (hide)="handleHide()"
    >
      <div class="modal-header">
        <div class="modal-title h4">{{ title() }}</div>
        @if (!loading()) {
          <button type="button" class="btn-close" aria-label="Close" (click)="handleHide()"></button>
        }
      </div>
      <div class="modal-body">
        @if (message()) {
          {{ message() }}
        }
        <ng-content />
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-outline-secondary" (click)="handleHide()" [disabled]="loading()">
          <i class="bi bi-x-circle me-1"></i>
          {{ cancelLabel() }}
        </button>
        <button type="button" class="btn" [class]="'btn-' + confirmVariant()" (click)="handleConfirm()" [disabled]="loading()">
          @if (loading()) {
            <span class="spinner-border spinner-border-sm me-1" role="status"></span>
            {{ loadingLabel() }}
          } @else {
            <i class="bi me-1" [class]="confirmIcon()"></i>
            {{ confirmLabel() }}
          }
        </button>
      </div>
    </app-modal>
  `,
})
export class ConfirmModalComponent {
  readonly show = input<boolean>(false);
  readonly title = input.required<string>();
  readonly message = input<string | null>(null);
  readonly confirmLabel = input<string>('Confirmar');
  readonly cancelLabel = input<string>('Cancelar');
  readonly confirmVariant = input<ConfirmVariant>('danger');
  readonly confirmIcon = input<string>('bi-check-circle');
  readonly loadingLabel = input<string>('Procesando…');
  readonly loading = input<boolean>(false);
  readonly size = input<'sm' | 'lg' | 'xl' | undefined>(undefined);

  readonly confirm = output<void>();
  readonly hide = output<void>();

  protected handleConfirm(): void {
    if (this.loading()) return;
    this.confirm.emit();
  }

  protected handleHide(): void {
    if (this.loading()) return;
    this.hide.emit();
  }
}
