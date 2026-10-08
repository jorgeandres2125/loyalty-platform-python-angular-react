import { ChangeDetectionStrategy, Component, computed, input, output, signal } from '@angular/core';
import { ConfirmModalComponent } from './confirm-modal.component';

interface Mascota {
  nombre: string;
}

const EMPTY_MASCOTA: Mascota = { nombre: '' };

function parseMascotas(raw: string): Mascota[] {
  if (!raw) return [];
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return (parsed as unknown[]).map((item: unknown): Mascota => {
      const obj = (item ?? {}) as Record<string, unknown>;
      return { nombre: String(obj['nombre'] ?? '') };
    });
  } catch {
    return [];
  }
}

function tieneMascotaFromState(numeroMascotas: string): boolean {
  const trimmed: string = (numeroMascotas ?? '').trim();
  if (!trimmed) return false;
  return trimmed.toLowerCase() !== 'no';
}

export interface MascotasCambio {
  numeroMascotas: string;
  infoMascotas: string;
}

@Component({
  selector: 'app-tiene-mascota-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ConfirmModalComponent],
  template: `
    <div>
      <div class="d-flex flex-wrap align-items-center gap-4">
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="radio" id="tiene-mascota-no" name="tiene-mascota"
            [checked]="!tieneMascota()" (change)="setRespuesta('no')" />
          <label class="form-check-label" for="tiene-mascota-no">No</label>
        </div>
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="radio" id="tiene-mascota-si" name="tiene-mascota"
            [checked]="tieneMascota()" (change)="setRespuesta('si')" />
          <label class="form-check-label" for="tiene-mascota-si">
            Sí{{ tieneMascota() ? ' (' + mascotas().length + ')' : '' }}
          </label>
        </div>
      </div>

      @if (tieneMascota()) {
        <div class="mt-3">
          @for (mascota of mascotas(); track $index; let idx = $index) {
            <div class="hijos-row">
              <span class="hijo-index">Mascota {{ idx + 1 }}</span>
              <div class="row g-2 align-items-end">
                <div class="col-12 col-md">
                  <label class="form-label small mb-1">
                    <i class="bi bi-patch-heart me-1 text-danger"></i>Nombre
                  </label>
                  <input class="form-control" [value]="mascota.nombre" placeholder="Nombre de la mascota"
                    maxlength="100" (input)="updateMascota(idx, $any($event.target).value)" />
                </div>
                <div class="col-12 col-md-auto">
                  <button type="button" class="btn btn-outline-danger btn-sm w-100 hijo-remove"
                    (click)="idxAEliminar.set(idx)">
                    <i class="bi bi-trash me-1"></i>Eliminar
                  </button>
                </div>
              </div>
            </div>
          }
          <button type="button" class="btn btn-outline-danger btn-sm mt-3" (click)="addMascota()">
            <i class="bi bi-plus-circle me-1"></i>Agregar mascota
          </button>
        </div>
      }

      <app-confirm-modal
        [show]="idxAEliminar() !== null"
        title="Eliminar mascota"
        confirmLabel="Sí, eliminar"
        confirmIcon="bi-trash"
        (confirm)="confirmarEliminarMascota()"
        (hide)="idxAEliminar.set(null)"
      >
        @if (mascotaAEliminar(); as m) {
          ¿Seguro que quieres eliminar a
          <strong>{{ m.nombre || 'Mascota ' + ((idxAEliminar() ?? 0) + 1) }}</strong>?
          <br />
          <span class="text-muted small">Esta acción no se puede deshacer.</span>
        }
      </app-confirm-modal>
    </div>
  `,
})
export class TieneMascotaSelectorComponent {
  readonly numeroMascotas = input<string>('');
  readonly infoMascotas = input<string>('');
  readonly changed = output<MascotasCambio>();

  protected readonly tieneMascota = computed<boolean>(() =>
    tieneMascotaFromState(this.numeroMascotas()),
  );
  protected readonly mascotas = computed<Mascota[]>(() => parseMascotas(this.infoMascotas()));
  protected readonly idxAEliminar = signal<number | null>(null);
  protected readonly mascotaAEliminar = computed<Mascota | null>(() => {
    const idx = this.idxAEliminar();
    const mascotas = this.mascotas();
    return idx !== null && idx < mascotas.length ? mascotas[idx] : null;
  });

  private emitir(numeroMascotas: string, infoMascotas: string): void {
    this.changed.emit({ numeroMascotas, infoMascotas });
  }

  private emit(next: Mascota[]): void {
    if (next.length === 0) {
      this.emitir('No', '');
    } else {
      this.emitir('Si', JSON.stringify(next));
    }
  }

  protected setRespuesta(value: 'no' | 'si'): void {
    const mascotas = this.mascotas();
    if (value === 'no') {
      this.emitir('No', '');
    } else if (mascotas.length === 0) {
      this.emit([{ ...EMPTY_MASCOTA }]);
    } else {
      this.emitir('Si', JSON.stringify(mascotas));
    }
  }

  protected updateMascota(index: number, nombre: string): void {
    this.emit(this.mascotas().map((m, i) => (i === index ? { nombre } : m)));
  }

  protected addMascota(): void {
    this.emit([...this.mascotas(), { ...EMPTY_MASCOTA }]);
  }

  protected confirmarEliminarMascota(): void {
    const idx = this.idxAEliminar();
    if (idx === null) return;
    this.emit(this.mascotas().filter((_, i) => i !== idx));
    this.idxAEliminar.set(null);
  }
}
