import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'app-status-badge',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <span
      class="badge badge-role"
      [class]="active() ? 'bg-success bg-opacity-15 text-success' : 'bg-secondary bg-opacity-15 text-secondary'"
    >
      <i class="bi bi-circle-fill me-1 status-dot"></i>
      {{ active() ? labels()[0] : labels()[1] }}
    </span>
  `,
})
export class StatusBadgeComponent {
  readonly active = input.required<boolean>();
  readonly labels = input<[string, string]>(['Activo', 'Inactivo']);
}
