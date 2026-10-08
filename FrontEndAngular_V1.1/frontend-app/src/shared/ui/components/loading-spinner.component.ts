import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'app-loading-spinner',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (fullPage()) {
      <div
        class="d-flex flex-column align-items-center justify-content-center"
        style="min-height: 60vh"
        role="status"
        [attr.aria-label]="text()"
      >
        <div class="spinner-border mb-3" style="width: 2.5rem; height: 2.5rem; color: #FF0026"></div>
        <p class="text-muted small mb-0">{{ text() }}</p>
      </div>
    } @else {
      <span class="spinner-border spinner-border-sm" role="status" [attr.aria-label]="text()"></span>
    }
  `,
})
export class LoadingSpinnerComponent {
  readonly fullPage = input<boolean>(false);
  readonly text = input<string>('Cargando...');
}
