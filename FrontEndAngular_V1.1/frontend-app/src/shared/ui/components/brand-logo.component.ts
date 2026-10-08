import { ChangeDetectionStrategy, Component, input } from '@angular/core';

export const LOGO_SRC = 'assets/LOGO_CLEAR.png' as const;

@Component({
  selector: 'app-brand-logo',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { style: 'display: contents' },
  template: `
    <img
      [src]="src"
      alt="SUFI Contigo"
      [height]="height()"
      draggable="false"
      [class]="className()"
      style="display: block; object-fit: contain"
    />
  `,
})
export class BrandLogoComponent {
  protected readonly src = LOGO_SRC;
  readonly height = input<number>(40);
  readonly className = input<string>('');
}
