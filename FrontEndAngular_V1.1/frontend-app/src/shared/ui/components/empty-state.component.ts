import { ChangeDetectionStrategy, Component, input } from '@angular/core';

/** Estado vacío. La acción opcional se proyecta como contenido. */
@Component({
  selector: 'app-empty-state',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="text-center py-5 px-4">
      <i class="bi" [class]="icon()" style="font-size: 3rem; color: #B2BFCC"></i>
      <h6 class="mt-3 fw-semibold" style="color: #333241">{{ title() }}</h6>
      @if (description()) {
        <p class="text-muted small mb-3">{{ description() }}</p>
      }
      <ng-content />
    </div>
  `,
})
export class EmptyStateComponent {
  readonly icon = input<string>('bi-inbox');
  readonly title = input.required<string>();
  readonly description = input<string | undefined>(undefined);
}
