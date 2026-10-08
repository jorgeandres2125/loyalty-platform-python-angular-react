import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  afterNextRender,
  effect,
  inject,
  input,
  model,
  signal,
  untracked,
  viewChild,
} from '@angular/core';
import TomSelect from 'tom-select';
import type { TomSelectOption } from './tom-select-field.component';

function aArreglo(raw: unknown): string[] {
  if (Array.isArray(raw)) return raw.map((item) => String(item));
  return raw ? [String(raw)] : [];
}

/** Select múltiple con búsqueda (Tom Select). Soporta `[(value)]`. */
@Component({
  selector: 'app-tom-select-multi-field',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<select #el [id]="id()" [required]="required()" multiple class="form-select"></select>`,
})
export class TomSelectMultiFieldComponent {
  readonly id = input.required<string>();
  readonly options = input.required<TomSelectOption[]>();
  readonly value = model<string[]>([]);
  readonly placeholder = input<string>('— Seleccionar —');
  readonly disabled = input<boolean>(false);
  readonly required = input<boolean>(false);
  readonly maxItems = input<number | null>(null);
  readonly maxOptions = input<number | undefined>(undefined);

  private readonly el = viewChild.required<ElementRef<HTMLSelectElement>>('el');
  private readonly ts = signal<TomSelect | null>(null);

  constructor() {
    afterNextRender(() => {
      const options: TomSelectOption[] = untracked(this.options);
      const ts = new TomSelect(this.el().nativeElement, {
        plugins: ['remove_button'],
        valueField: 'value',
        labelField: 'label',
        searchField: ['label'],
        placeholder: untracked(this.placeholder),
        maxItems: untracked(this.maxItems) ?? undefined,
        maxOptions: untracked(this.maxOptions) ?? options.length,
        options: options.map((o) => ({ value: o.value, label: o.label })),
        items: untracked(this.value),
        onChange: (v: unknown) => {
          if (Array.isArray(v)) {
            this.value.set(v.map((item) => String(item)));
          } else if (typeof v === 'string' && v !== '') {
            this.value.set([v]);
          } else {
            this.value.set([]);
          }
        },
      } as never);
      this.ts.set(ts);
    });
    inject(DestroyRef).onDestroy(() => {
      this.ts()?.destroy();
    });

    // Sincroniza opciones cuando cambian (sin destruir la instancia).
    effect(() => {
      const options: TomSelectOption[] = this.options();
      const maxOptions: number | undefined = this.maxOptions();
      const ts = this.ts();
      if (!ts) return;
      untracked(() => {
        ts.clearOptions();
        options.forEach((o) => ts.addOption({ value: o.value, label: o.label }));
        // Re-aplica maxOptions: la lista activa real es la fuente de verdad.
        ts.settings.maxOptions = maxOptions ?? options.length;
        ts.refreshOptions(false);
        // Mantener solo los valores que siguen siendo válidos.
        const valid: string[] = this.value().filter((val) => options.some((o) => o.value === val));
        ts.setValue(valid, true);
      });
    });

    // Sincroniza valores desde fuera (carga de edición, reset).
    effect(() => {
      const value: string[] = this.value();
      const ts = this.ts();
      if (!ts) return;
      const curArr: string[] = aArreglo(ts.getValue());
      const sameItems: boolean =
        curArr.length === value.length && curArr.every((item) => value.includes(item));
      if (!sameItems) {
        ts.setValue(value, true);
      }
    });

    effect(() => {
      const disabled: boolean = this.disabled();
      const ts = this.ts();
      if (!ts) return;
      if (disabled) ts.disable();
      else ts.enable();
    });
  }
}
