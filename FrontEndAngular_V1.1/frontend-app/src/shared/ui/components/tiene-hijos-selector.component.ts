import { ChangeDetectionStrategy, Component, computed, input, output, signal } from '@angular/core';
import { ConfirmModalComponent } from './confirm-modal.component';

export interface Hijo {
  nombre: string;
  genero: 'M' | 'F' | '';
  fecha_nacimiento: string;
}

const EMPTY_HIJO: Hijo = { nombre: '', genero: '', fecha_nacimiento: '' };

function parseHijos(raw: string): Hijo[] {
  if (!raw) return [];
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.map((item: unknown): Hijo => {
      const obj = (item ?? {}) as Record<string, unknown>;
      const generoRaw: string = String(obj['genero'] ?? '').toUpperCase();
      const genero: 'M' | 'F' | '' = generoRaw === 'M' || generoRaw === 'F' ? generoRaw : '';
      return {
        nombre: String(obj['nombre'] ?? ''),
        genero,
        fecha_nacimiento: String(obj['fecha_nacimiento'] ?? ''),
      };
    });
  } catch {
    return [];
  }
}

function tieneHijosFromState(numeroHijos: string): boolean {
  const trimmed: string = (numeroHijos ?? '').trim();
  if (!trimmed) return false;
  if (trimmed.toLowerCase() === 'no') return false;
  return true;
}

export interface HijosCambio {
  numeroHijos: string;
  infoHijos: string;
}

@Component({
  selector: 'app-tiene-hijos-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ConfirmModalComponent],
  template: `
    <div>
      <div class="d-flex flex-wrap align-items-center gap-4">
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="radio" id="tiene-hijos-no" name="tiene-hijos"
            [checked]="!tieneHijos()" (change)="setRespuesta('no')" />
          <label class="form-check-label" for="tiene-hijos-no">No</label>
        </div>
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="radio" id="tiene-hijos-si" name="tiene-hijos"
            [checked]="tieneHijos()" (change)="setRespuesta('si')" />
          <label class="form-check-label" for="tiene-hijos-si">
            Sí, ¿Cuántos?{{ tieneHijos() ? ' (' + hijos().length + ')' : '' }}
          </label>
        </div>
      </div>

      @if (tieneHijos()) {
        <div class="mt-3">
          @for (h of hijos(); track $index; let idx = $index) {
            <div class="hijos-row">
              <span class="hijo-index">Hijo {{ idx + 1 }}</span>
              <div class="row g-2 align-items-end">
                <div class="col-12 col-md-5">
                  <label class="form-label small mb-1">
                    <i class="bi bi-person me-1 text-danger"></i>Nombre
                  </label>
                  <input class="form-control" [value]="h.nombre" placeholder="Nombre completo" maxlength="120"
                    (input)="updateHijo(idx, 'nombre', $any($event.target).value)" />
                </div>
                <div class="col-6 col-md-2">
                  <label class="form-label small mb-1">
                    <i class="bi bi-gender-ambiguous me-1 text-danger"></i>Género
                  </label>
                  <select class="form-select" [value]="h.genero"
                    (change)="updateHijo(idx, 'genero', $any($event.target).value)">
                    <option value="">Seleccione...</option>
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </select>
                </div>
                <div class="col-6 col-md-3">
                  <label class="form-label small mb-1">
                    <i class="bi bi-calendar-date me-1 text-danger"></i>Fecha nacimiento
                  </label>
                  <input class="form-control" type="date" [value]="h.fecha_nacimiento"
                    (input)="updateHijo(idx, 'fecha_nacimiento', $any($event.target).value)" />
                </div>
                <div class="col-12 col-md-2">
                  <button type="button" class="btn btn-outline-danger btn-sm w-100 hijo-remove"
                    (click)="idxAEliminar.set(idx)" title="Eliminar hijo">
                    <i class="bi bi-trash me-1"></i>Eliminar
                  </button>
                </div>
              </div>
            </div>
          }
          <button type="button" class="btn btn-outline-danger btn-sm mt-3" (click)="addHijo()">
            <i class="bi bi-plus-circle me-1"></i>Agregar hijo
          </button>
        </div>
      }

      <app-confirm-modal
        [show]="idxAEliminar() !== null"
        title="Eliminar hijo"
        confirmLabel="Sí, eliminar"
        confirmIcon="bi-trash"
        (confirm)="confirmarEliminarHijo()"
        (hide)="idxAEliminar.set(null)"
      >
        @if (hijoAEliminar(); as hijo) {
          ¿Seguro que quieres eliminar a
          <strong>{{ hijo.nombre || 'Hijo ' + ((idxAEliminar() ?? 0) + 1) }}</strong>?
          <br />
          <span class="text-muted small">Esta acción no se puede deshacer.</span>
        }
      </app-confirm-modal>
    </div>
  `,
})
export class TieneHijosSelectorComponent {
  readonly numeroHijos = input<string>('');
  readonly infoHijos = input<string>('');
  readonly changed = output<HijosCambio>();

  protected readonly tieneHijos = computed<boolean>(() => tieneHijosFromState(this.numeroHijos()));
  protected readonly hijos = computed<Hijo[]>(() => parseHijos(this.infoHijos()));
  protected readonly idxAEliminar = signal<number | null>(null);
  protected readonly hijoAEliminar = computed<Hijo | null>(() => {
    const idx = this.idxAEliminar();
    const hijos = this.hijos();
    return idx !== null && idx < hijos.length ? hijos[idx] : null;
  });

  private emitir(numeroHijos: string, infoHijos: string): void {
    this.changed.emit({ numeroHijos, infoHijos });
  }

  private emit(nextHijos: Hijo[]): void {
    if (nextHijos.length === 0) {
      this.emitir('No', '');
      return;
    }
    this.emitir(String(nextHijos.length), JSON.stringify(nextHijos));
  }

  protected setRespuesta(value: 'no' | 'si'): void {
    const hijos = this.hijos();
    if (value === 'no') {
      this.emitir('No', '');
    } else if (hijos.length === 0) {
      this.emit([{ ...EMPTY_HIJO }]);
    } else {
      // Ya tiene hijos cargados: solo sincroniza el conteo.
      this.emitir(String(hijos.length), JSON.stringify(hijos));
    }
  }

  protected updateHijo(index: number, field: keyof Hijo, value: string): void {
    const next: Hijo[] = this.hijos().map((h, i) => {
      if (i !== index) return h;
      if (field === 'genero') {
        const norm: string = value.toUpperCase();
        const genero: 'M' | 'F' | '' = norm === 'M' || norm === 'F' ? norm : '';
        return { ...h, genero };
      }
      return { ...h, [field]: value };
    });
    this.emit(next);
  }

  protected addHijo(): void {
    this.emit([...this.hijos(), { ...EMPTY_HIJO }]);
  }

  protected confirmarEliminarHijo(): void {
    const idx = this.idxAEliminar();
    if (idx === null) return;
    this.emit(this.hijos().filter((_, i) => i !== idx));
    this.idxAEliminar.set(null);
  }
}
