import { ChangeDetectionStrategy, Component, computed, inject, input } from '@angular/core';
import { ToastItemComponent } from './toast-item.component';
import { ToastService, type ToastPosition } from './toast.service';

const CLASES_POSICION: Record<ToastPosition, string> = {
  'top-start': 'top-0 start-0',
  'top-center': 'top-0 start-50 translate-middle-x',
  'top-end': 'top-0 end-0',
  'middle-start': 'top-50 start-0 translate-middle-y',
  'middle-center': 'top-50 start-50 translate-middle',
  'middle-end': 'top-50 end-0 translate-middle-y',
  'bottom-start': 'bottom-0 start-0',
  'bottom-center': 'bottom-0 start-50 translate-middle-x',
  'bottom-end': 'bottom-0 end-0',
};

/** Apila los toasts globales en un unico contenedor (equivalente a `ToastStack`). */
@Component({
  selector: 'app-toast-stack',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ToastItemComponent],
  template: `
    <div class="toast-container position-fixed p-3" [class]="clasePosicion()" style="z-index: 1090">
      @for (t of toast.toasts(); track t.id) {
        <app-toast-item
          [title]="t.title ?? 'Notificacion'"
          [message]="t.message ?? ''"
          [detail]="t.detail"
          [bgColor]="t.bgColor ?? 'primary'"
          [icon]="t.icon"
          [delay]="t.delay ?? 10000"
          [autohide]="t.autohide ?? true"
          (closed)="toast.closeToast(t.id)"
        />
      }
    </div>
  `,
})
export class ToastStackComponent {
  protected readonly toast = inject(ToastService);
  readonly position = input<ToastPosition>('top-end');
  protected readonly clasePosicion = computed<string>(() => CLASES_POSICION[this.position()]);
}
