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

export interface OpcionBuscador {
  value: string;
  text: string;
}

type TomSettings = NonNullable<ConstructorParameters<typeof TomSelect>[1]>;

/**
 * Select con búsqueda (Tom Select) usado en los formularios de registro/perfil
 * (departamento, ciudad, canal, oficina, profesión, EPS, AFP…). Replica el uso directo
 * de Tom Select del proyecto React:
 * - la instancia se recrea cuando cambian las opciones o el placeholder;
 * - al vaciar la selección se reabre el desplegable con el texto limpio;
 * - `locked` bloquea la búsqueda (Tom Select `lock()`) y `disabled` deshabilita.
 * Soporta `[(value)]`.
 */
@Component({
  selector: 'app-tom-select-buscador',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<select #el class="form-select" [attr.id]="selectId()"></select>`,
})
export class TomSelectBuscadorComponent {
  readonly options = input.required<OpcionBuscador[]>();
  readonly value = model<string>('');
  readonly placeholder = input<string>('');
  readonly locked = input<boolean>(false);
  readonly disabled = input<boolean>(false);
  /** Muestra "Sin resultados" cuando la búsqueda no coincide. */
  readonly sinResultados = input<boolean>(false);
  /** Al vaciar la selección, reabre el desplegable con el texto limpio. */
  readonly reabrirAlLimpiar = input<boolean>(true);
  readonly selectId = input<string | null>(null);

  private readonly el = viewChild.required<ElementRef<HTMLSelectElement>>('el');
  private readonly ts = signal<TomSelect | null>(null);
  private readonly montado = signal<boolean>(false);

  constructor() {
    afterNextRender(() => this.montado.set(true));
    inject(DestroyRef).onDestroy(() => this.ts()?.destroy());

    // (Re)crea la instancia cuando cambian las opciones o el placeholder.
    effect(() => {
      if (!this.montado()) return;
      const options: OpcionBuscador[] = this.options();
      const placeholder: string = this.placeholder();
      const sinResultados: boolean = this.sinResultados();
      const reabrir: boolean = this.reabrirAlLimpiar();
      untracked(() => {
        this.ts()?.destroy();
        const valor: string = this.value() ?? '';
        const settings: TomSettings = {
          valueField: 'value',
          labelField: 'text',
          searchField: ['text'],
          options: options.map((o) => ({ value: o.value, text: o.text })),
          items: valor ? [valor] : [],
          placeholder,
          maxOptions: null as unknown as number,
          onChange: (v: string) => {
            this.value.set(v ?? '');
            if (!v && reabrir) {
              setTimeout(() => {
                const ts = this.ts();
                if (!ts) return;
                ts.setTextboxValue('');
                ts.refreshOptions(false);
                ts.open();
              }, 0);
            }
          },
        };
        if (sinResultados) {
          settings.render = {
            no_results: () => '<div class="no-results px-3 py-2 text-muted small">Sin resultados</div>',
          };
        }
        const ts = new TomSelect(this.el().nativeElement, settings);
        this.aplicarEstado(ts, this.locked(), this.disabled());
        this.ts.set(ts);
      });
    });

    // Sincroniza el valor cuando cambia desde fuera (modo edición, reset).
    effect(() => {
      const valor: string = this.value() ?? '';
      const ts = this.ts();
      if (!ts) return;
      if (String(ts.getValue() ?? '') !== valor) ts.setValue(valor, true);
    });

    // Bloqueo / habilitación.
    effect(() => {
      const locked: boolean = this.locked();
      const disabled: boolean = this.disabled();
      const ts = this.ts();
      if (!ts) return;
      this.aplicarEstado(ts, locked, disabled);
    });
  }

  private aplicarEstado(ts: TomSelect, locked: boolean, disabled: boolean): void {
    if (disabled) ts.disable();
    else ts.enable();
    if (locked) ts.lock();
    else ts.unlock();
  }
}
