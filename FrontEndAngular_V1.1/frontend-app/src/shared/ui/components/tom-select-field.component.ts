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

export interface TomSelectOption {
  value: string;
  label: string;
}

/** Select con búsqueda (Tom Select) de un solo valor. Soporta `[(value)]`. */
@Component({
  selector: 'app-tom-select-field',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<select #el [id]="id()" [required]="required()" class="form-select"></select>`,
})
export class TomSelectFieldComponent {
  readonly id = input.required<string>();
  readonly options = input.required<TomSelectOption[]>();
  readonly value = model<string>('');
  readonly placeholder = input<string>('— Seleccionar —');
  readonly disabled = input<boolean>(false);
  readonly required = input<boolean>(false);

  private readonly el = viewChild.required<ElementRef<HTMLSelectElement>>('el');
  private readonly ts = signal<TomSelect | null>(null);

  constructor() {
    // Inicializa una sola vez, tras el primer render.
    afterNextRender(() => {
      const value: string = untracked(this.value);
      const ts = new TomSelect(this.el().nativeElement, {
        valueField: 'value',
        labelField: 'label',
        searchField: ['label'],
        placeholder: untracked(this.placeholder),
        options: untracked(this.options).map((o) => ({ value: o.value, label: o.label })),
        items: value ? [value] : [],
        onChange: (v: unknown) => {
          this.value.set(typeof v === 'string' ? v : '');
        },
      });
      this.ts.set(ts);
    });
    inject(DestroyRef).onDestroy(() => {
      this.ts()?.destroy();
    });

    // Sincroniza opciones cuando cambian (ej. cambio de departamento).
    effect(() => {
      const options: TomSelectOption[] = this.options();
      const ts = this.ts();
      if (!ts) return;
      untracked(() => {
        const value: string = this.value();
        ts.clearOptions();
        options.forEach((o) => ts.addOption({ value: o.value, label: o.label }));
        ts.refreshOptions(false);
        // Restaura el valor si todavía es válido; de lo contrario limpia.
        if (value && options.some((o) => o.value === value)) {
          ts.setValue(value, true);
        } else {
          ts.clear(true);
        }
      });
    });

    // Sincroniza valor desde fuera (carga de edición, reset).
    effect(() => {
      const value: string = this.value() ?? '';
      const ts = this.ts();
      if (!ts) return;
      const cur: string = String(ts.getValue() ?? '');
      if (cur !== value) {
        ts.setValue(value || '', true);
      }
    });

    // Sincroniza estado habilitado/deshabilitado.
    effect(() => {
      const disabled: boolean = this.disabled();
      const ts = this.ts();
      if (!ts) return;
      if (disabled) ts.disable();
      else ts.enable();
    });
  }
}
