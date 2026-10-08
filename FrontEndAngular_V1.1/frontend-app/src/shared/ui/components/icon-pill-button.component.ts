import { ChangeDetectionStrategy, Component, computed, input, output } from '@angular/core';

export type IconPillColor =
  | 'red'
  | 'navy'
  | 'blue'
  | 'gold'
  | 'yellow'
  | 'dark-navy'
  | 'teal'
  | 'green'
  | 'gray'
  | 'orange'
  | 'purple';

export interface IconPillCustomColor {
  base: string;
  dark: string;
}

@Component({
  selector: 'app-icon-pill-button',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { style: 'display: contents' },
  template: `
    <button
      type="button"
      [class]="clases()"
      [attr.aria-pressed]="selected()"
      [attr.aria-label]="ariaLabel() ?? label()"
      [disabled]="disabled()"
      (click)="pressed.emit()"
      (keydown)="handleKey($event)"
      [style.--icon-pill-color]="customColor()?.base"
      [style.--icon-pill-color-dark]="customColor()?.dark"
    >
      <span class="icon-pill__icon" aria-hidden="true">
        <i class="bi" [class]="icon()"></i>
      </span>
      <span class="icon-pill__label">{{ label() }}</span>
    </button>
  `,
})
export class IconPillButtonComponent {
  readonly label = input.required<string>();
  /** Clase de Bootstrap Icons (p. ej. `bi-book-fill`). */
  readonly icon = input.required<string>();
  readonly color = input<IconPillColor>('blue');
  readonly customColor = input<IconPillCustomColor | undefined>(undefined);
  readonly selected = input<boolean>(false);
  readonly disabled = input<boolean>(false);
  readonly ariaLabel = input<string | undefined>(undefined);
  readonly className = input<string>('');

  readonly pressed = output<void>();

  protected readonly clases = computed<string>(() => {
    const colorClass: string = this.customColor() ? 'has-custom-color' : `icon-pill--${this.color()}`;
    return [
      'icon-pill',
      colorClass,
      this.selected() ? 'is-selected' : '',
      this.disabled() ? 'is-disabled' : '',
      this.className(),
    ]
      .filter(Boolean)
      .join(' ');
  });

  protected handleKey(e: KeyboardEvent): void {
    if (this.disabled()) return;
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      this.pressed.emit();
    }
  }
}
