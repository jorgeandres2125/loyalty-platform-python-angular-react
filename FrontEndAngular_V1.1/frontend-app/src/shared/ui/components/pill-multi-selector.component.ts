import { ChangeDetectionStrategy, Component, computed, input, model } from '@angular/core';
import { IconPillButtonComponent, type IconPillColor } from './icon-pill-button.component';

export interface PillOption {
  value: string;
  label: string;
  icon: string;
}

/**
 * Modo de comparación del selector:
 * - `lower`: normaliza a minúsculas y guarda el valor normalizado (Hobbies, ConQuienVives).
 * - `ci`: compara sin distinguir mayúsculas y guarda el valor original de la opción
 *   (Premios, Propósitos, Temas a profundizar).
 * - `keys`: solo admite claves fijas de las opciones (Propósitos familiares).
 */
export type PillCompareMode = 'lower' | 'ci' | 'keys';

function normalizar(s: string, modo: PillCompareMode): string {
  const base: string = s.normalize('NFC').trim();
  return modo === 'lower' ? base.toLowerCase() : base;
}

function parseSelection(raw: string, modo: PillCompareMode): string[] {
  if (!raw) return [];
  try {
    const parsed: unknown = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed.map((v) => normalizar(String(v), modo));
  } catch {
    return raw
      .split(',')
      .map((s) => normalizar(s, modo))
      .filter(Boolean);
  }
  return [];
}

/**
 * Selector múltiple de "píldoras" con icono. El valor se serializa como JSON
 * (`["a","b"]`) o cadena vacía, igual que los selectores del proyecto React.
 * Base común de HobbiesSelector, PremiosSelector, Propositos*Selector, etc.
 */
@Component({
  selector: 'app-pill-multi-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [IconPillButtonComponent],
  template: `
    <div class="row g-2">
      @for (opt of options(); track opt.value) {
        <div [class]="colClass()">
          <app-icon-pill-button
            [label]="opt.label"
            [icon]="opt.icon"
            [color]="color()"
            [selected]="estaSeleccionado(opt.value)"
            (pressed)="toggle(opt.value)"
          />
        </div>
      }
    </div>
  `,
})
export class PillMultiSelectorComponent {
  readonly options = input.required<readonly PillOption[]>();
  readonly color = input<IconPillColor>('blue');
  readonly mode = input<PillCompareMode>('ci');
  readonly colClass = input<string>('col-12 col-sm-6 col-md');
  readonly value = model<string>('');

  private readonly selected = computed<string[]>(() => {
    const lista: string[] = parseSelection(this.value(), this.mode());
    if (this.mode() === 'keys') {
      const claves: Set<string> = new Set(this.options().map((o) => o.value));
      return lista.filter((v) => claves.has(v));
    }
    return lista;
  });

  protected estaSeleccionado(optValue: string): boolean {
    const modo: PillCompareMode = this.mode();
    const sel: string[] = this.selected();
    if (modo === 'ci') {
      const optNorm: string = normalizar(optValue, modo).toLowerCase();
      return sel.some((v) => v.toLowerCase() === optNorm);
    }
    return sel.includes(normalizar(optValue, modo));
  }

  protected toggle(optValue: string): void {
    const modo: PillCompareMode = this.mode();
    const sel: string[] = this.selected();
    let next: string[];
    if (modo === 'ci') {
      const norm: string = optValue.toLowerCase();
      const isSelected: boolean = sel.some((v) => v.toLowerCase() === norm);
      next = isSelected ? sel.filter((v) => v.toLowerCase() !== norm) : [...sel, optValue];
    } else {
      const norm: string = normalizar(optValue, modo);
      next = sel.includes(norm) ? sel.filter((v) => v !== norm) : [...sel, norm];
    }
    this.value.set(next.length === 0 ? '' : JSON.stringify(next));
  }
}
