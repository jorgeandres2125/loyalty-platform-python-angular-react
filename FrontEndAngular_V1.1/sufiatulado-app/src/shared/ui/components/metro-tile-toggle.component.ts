import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  computed,
  inject,
  input,
  output,
  signal,
} from '@angular/core';

export type MetroTileSize = 'small' | 'medium' | 'wide';

export type MetroTileColor =
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
  | 'orange-deep'
  | 'amber'
  | 'cyan'
  | 'cyan-deep'
  | 'purple'
  | 'violet'
  | 'magenta';

export interface MetroTileCustomColor {
  base: string;
  dark: string;
}

let secuencia = 0;

/** Duraciones/curva equivalentes a las variantes de framer-motion del original. */
const DURACION_CIERRE_MS = 320;

/**
 * Tile tipo "Metro" desplegable (equivalente a `MetroTileToggle`). Las animaciones de
 * framer-motion se reemplazan por transiciones CSS (expansión con grid-template-rows,
 * fade/slide del contenido y escala del encabezado en hover/tap).
 */
@Component({
  selector: 'app-metro-tile-toggle',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { style: 'display: contents' },
  template: `
    <div
      [class]="clases()"
      [style.--metro-tile-color]="customColor()?.base"
      [style.--metro-tile-color-dark]="customColor()?.dark"
    >
      <button
        type="button"
        class="metro-tile__header metro-tile__header--anim"
        [attr.aria-expanded]="open()"
        [attr.aria-controls]="bodyId"
        role="button"
        (click)="toggle()"
      >
        <span class="metro-tile__icon" aria-hidden="true">
          <i class="bi" [class]="icon()"></i>
        </span>
        <span class="metro-tile__titles">
          <span class="metro-tile__title">{{ title() }}</span>
          @if (subtitle()) {
            <span class="metro-tile__subtitle">{{ subtitle() }}</span>
          }
        </span>
        @if (showBadge()) {
          <span class="metro-tile__badge">{{ badge() }}</span>
        }
        <span class="metro-tile__chevron" aria-hidden="true">
          <i class="bi bi-chevron-down"></i>
        </span>
      </button>

      @if (rendered()) {
        <section
          [id]="bodyId"
          class="metro-tile__body metro-tile__body--anim"
          [class.is-expanded]="expanded()"
          [attr.aria-hidden]="!open()"
        >
          <div class="metro-tile__body-inner">
            <div class="metro-tile__content metro-tile__content--anim">
              <ng-content />
            </div>
            <div class="metro-tile__footer">
              @if (hasSave()) {
                <button
                  type="button"
                  class="metro-tile__save"
                  (click)="save.emit()"
                  [disabled]="saving() || saveDisabled()"
                >
                  @if (saving()) {
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Guardando…
                  } @else {
                    <i class="bi bi-check-lg"></i>
                    {{ saveLabel() }}
                  }
                </button>
              }
              <button type="button" class="metro-tile__close" (click)="cerrar()">
                <i class="bi bi-x-lg"></i>
                {{ closeLabel() }}
              </button>
            </div>
          </div>
        </section>
      }
    </div>
  `,
  styles: `
    .metro-tile__header--anim {
      transition:
        transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1),
        box-shadow 0.25s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .metro-tile__header--anim:hover {
      transform: translateY(-2px) scale(1.02);
    }
    .metro-tile__header--anim:active {
      transform: scale(0.98);
    }
    .metro-tile__body--anim {
      display: grid;
      grid-template-rows: 0fr;
      opacity: 0;
      transition:
        grid-template-rows 0.32s cubic-bezier(0.22, 1, 0.36, 1),
        opacity 0.32s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .metro-tile__body--anim.is-expanded {
      grid-template-rows: 1fr;
      opacity: 1;
      transition-duration: 0.42s;
    }
    .metro-tile__body-inner {
      min-height: 0;
      overflow: hidden;
    }
    .metro-tile__content--anim {
      opacity: 0;
      transform: translateY(12px);
      transition:
        opacity 0.18s ease,
        transform 0.18s ease;
    }
    .is-expanded .metro-tile__content--anim {
      opacity: 1;
      transform: translateY(0);
      transition:
        opacity 0.32s cubic-bezier(0.22, 1, 0.36, 1) 0.08s,
        transform 0.32s cubic-bezier(0.22, 1, 0.36, 1) 0.08s;
    }
  `,
})
export class MetroTileToggleComponent {
  readonly title = input.required<string>();
  readonly icon = input.required<string>();
  readonly subtitle = input<string | undefined>(undefined);
  readonly color = input<MetroTileColor>('red');
  readonly customColor = input<MetroTileCustomColor | undefined>(undefined);
  readonly size = input<MetroTileSize>('medium');
  readonly badge = input<number | string | null | undefined>(null);
  readonly defaultOpen = input<boolean>(false);
  readonly closeLabel = input<string>('Cerrar');
  readonly className = input<string>('');
  /** Muestra el botón Guardar (equivalente a pasar `onSave`). */
  readonly hasSave = input<boolean>(false);
  readonly saveLabel = input<string>('Guardar');
  readonly saving = input<boolean>(false);
  readonly saveDisabled = input<boolean>(false);

  readonly save = output<void>();

  protected readonly bodyId: string = `metro-tile-body-${++secuencia}`;

  /** Estado lógico (abierto/cerrado). */
  protected readonly open = signal<boolean>(false);
  /** El cuerpo sigue en el DOM durante la animación de cierre. */
  protected readonly rendered = signal<boolean>(false);
  /** Clase que dispara la transición de expansión. */
  protected readonly expanded = signal<boolean>(false);

  private timer: ReturnType<typeof setTimeout> | undefined;
  private inicializado = false;

  protected readonly clases = computed<string>(() => {
    const colorClass: string = this.customColor() ? 'has-custom-color' : `metro-tile--${this.color()}`;
    return [
      'metro-tile',
      colorClass,
      `metro-tile--${this.size()}`,
      this.open() ? 'is-open' : '',
      this.className(),
    ]
      .filter(Boolean)
      .join(' ');
  });

  protected readonly showBadge = computed<boolean>(() => {
    const badge = this.badge();
    return badge !== null && badge !== undefined && badge !== '' && badge !== 0;
  });

  constructor() {
    inject(DestroyRef).onDestroy(() => clearTimeout(this.timer));
    // `defaultOpen` solo se aplica una vez (como el useState inicial del original).
    queueMicrotask(() => {
      if (!this.inicializado && this.defaultOpen()) {
        this.inicializado = true;
        this.abrir(false);
      }
    });
  }

  protected toggle(): void {
    this.inicializado = true;
    if (this.open()) this.cerrar();
    else this.abrir(true);
  }

  private abrir(animar: boolean): void {
    clearTimeout(this.timer);
    this.open.set(true);
    this.rendered.set(true);
    if (animar) {
      requestAnimationFrame(() => requestAnimationFrame(() => this.expanded.set(true)));
    } else {
      this.expanded.set(true);
    }
  }

  protected cerrar(): void {
    clearTimeout(this.timer);
    this.open.set(false);
    this.expanded.set(false);
    this.timer = setTimeout(() => this.rendered.set(false), DURACION_CIERRE_MS);
  }
}
