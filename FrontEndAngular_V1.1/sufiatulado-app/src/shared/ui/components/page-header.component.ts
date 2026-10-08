import { ChangeDetectionStrategy, Component, inject, input } from '@angular/core';
import { Router } from '@angular/router';

/**
 * Encabezado de página. Las acciones se proyectan con el atributo `actions`:
 *   <app-page-header title="…"><button actions …>…</button></app-page-header>
 */
@Component({
  selector: 'app-page-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="page-header d-flex align-items-start justify-content-between gap-3 flex-wrap">
      <div class="d-flex align-items-center gap-2">
        @if (backTo()) {
          <button class="page-header__back" (click)="volver()" aria-label="Volver">
            <i class="bi bi-arrow-left"></i>
          </button>
        }
        <div>
          <h2 class="d-flex align-items-center gap-2">
            @if (icon()) {
              <i class="bi text-sufi-red" [class]="icon()" style="font-size: 1.5rem"></i>
            }
            {{ title() }}
          </h2>
          @if (subtitle()) {
            <p class="page-subtitle">{{ subtitle() }}</p>
          }
        </div>
      </div>
      <div class="page-header__actions d-flex gap-2 flex-wrap">
        <ng-content select="[actions]" />
      </div>
    </div>
  `,
  styles: `.page-header__actions:empty { display: none !important; }`,
})
export class PageHeaderComponent {
  private readonly router = inject(Router);
  readonly title = input.required<string>();
  readonly subtitle = input<string | undefined>(undefined);
  readonly icon = input<string | undefined>(undefined);
  readonly backTo = input<string | undefined>(undefined);

  protected volver(): void {
    const destino = this.backTo();
    if (destino) void this.router.navigateByUrl(destino);
  }
}
