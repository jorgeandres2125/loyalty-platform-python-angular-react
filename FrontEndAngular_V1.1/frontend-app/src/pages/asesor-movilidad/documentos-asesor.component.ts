import { ChangeDetectionStrategy, Component, input, signal } from '@angular/core';
import type { DocumentoEditPayload, DocumentoItem } from '../../features/documentos/model/types';
import { injectDocumentosAsesor, injectEditarDocumento } from '../../features/documentos/model/queries';
import { leerInput } from '../../shared/lib/inputs';

export const ESTADOS_DOCUMENTO: ReadonlyArray<{ value: string; label: string; bg: string }> = [
  { value: 'pendiente', label: 'Pendiente', bg: 'warning' },
  { value: 'revision', label: 'Revisión', bg: 'info' },
  { value: 'aprobado', label: 'Aprobado', bg: 'success' },
];

export function estadoBadgeBg(estado: string): string {
  return ESTADOS_DOCUMENTO.find((e) => e.value === estado.toLowerCase())?.bg ?? 'secondary';
}

export function estadoLabel(estado: string): string {
  return ESTADOS_DOCUMENTO.find((e) => e.value === estado.toLowerCase())?.label ?? estado;
}

const pad = (n: number): string => String(n).padStart(2, '0');

function formatFechaInput(value: string | null): string {
  if (!value) return '';
  const date: Date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function formatFechaDisplay(value: string | null): string {
  if (!value) return '—';
  const date: Date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

interface DocumentoEditState {
  did: number;
  nombre: string;
  estado: string;
  fecha: string;
}

/** Documentos de un asesor con edición en línea (nombre, estado y fecha de alta). */
@Component({
  selector: 'app-documentos-asesor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (docs.isLoading()) {
      <div class="text-center py-3">
        <span class="spinner-border spinner-border-sm text-danger" role="status"></span>
      </div>
    } @else if (!docs.data() || docs.data()!.length === 0) {
      <div class="text-center py-3 text-muted small">
        <i class="bi bi-inbox me-2"></i>
        Sin documentos cargados para este asesor
      </div>
    } @else {
      <div class="p-3" style="background: #f8f9fa">
        <table class="table table-sm table-hover mb-0 bg-white">
          <thead class="table-light">
            <tr>
              <th>Id</th>
              <th>Tipo de documento</th>
              <th>Documento</th>
              <th>Estado</th>
              <th class="text-center">Versión</th>
              <th>Fecha Alta</th>
              <th class="text-center">Operación</th>
            </tr>
          </thead>
          <tbody>
            @for (doc of docs.data(); track doc.did) {
              <tr>
                <td class="font-monospace">{{ doc.did }}</td>
                <td>{{ doc.tipo_nombre }}</td>
                <td class="font-monospace">{{ doc.nombre }}</td>
                <td><span class="badge" [class]="'bg-' + badgeBg(doc.estado)">{{ label(doc.estado) }}</span></td>
                <td class="text-center">{{ doc.version }}</td>
                <td>{{ fechaDisplay(doc.fecha) }}</td>
                <td class="text-center">
                  <button type="button" class="btn btn-sm" [class]="editId() === doc.did ? 'btn-secondary' : 'btn-outline-primary'"
                    (click)="editId() === doc.did ? cancelarEdicion() : abrirEdicion(doc)">
                    <i class="bi me-1" [class]="editId() === doc.did ? 'bi-x-lg' : 'bi-pencil'"></i>
                    {{ editId() === doc.did ? 'Cerrar' : 'Editar' }}
                  </button>
                </td>
              </tr>
            }
          </tbody>
        </table>

        @if (edit(); as e) {
          <div class="mt-3">
            <div class="card border-primary">
              <div class="card-body">
                <h6 class="fw-semibold mb-3">
                  <i class="bi bi-pencil-square me-2 text-primary"></i>
                  Editar documento #{{ e.did }}
                </h6>
                @if (errorMsg()) {
                  <div class="alert alert-danger alert-dismissible py-2">
                    {{ errorMsg() }}
                    <button type="button" class="btn-close" aria-label="Close" (click)="errorMsg.set('')"></button>
                  </div>
                }
                <div class="row g-3">
                  <div class="col-md-4">
                    <label class="form-label small fw-semibold mb-1">Id Documento</label>
                    <input class="form-control font-monospace" [value]="e.did" readonly disabled />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small fw-semibold mb-1">Número documento asesor</label>
                    <input class="form-control font-monospace" [value]="numeroDocumento()" readonly disabled />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small fw-semibold mb-1">Nombre archivo</label>
                    <input class="form-control" [value]="e.nombre" (input)="patch({ nombre: leer($event) })" />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small fw-semibold mb-1">Versión</label>
                    <input class="form-control" [value]="version(e.did)" readonly disabled />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small fw-semibold mb-1">Estado</label>
                    <select class="form-select" (change)="patch({ estado: $any($event.target).value })">
                      @for (es of estados; track es.value) {
                        <option [value]="es.value" [selected]="es.value === e.estado">{{ es.label }}</option>
                      }
                    </select>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small fw-semibold mb-1">Fecha de alta</label>
                    <input class="form-control" type="datetime-local" [value]="e.fecha" (input)="patch({ fecha: leer($event) })" />
                  </div>
                </div>
                <div class="d-flex justify-content-end gap-2 mt-3">
                  <button type="button" class="btn btn-outline-secondary" (click)="cancelarEdicion()" [disabled]="editar.isPending()">
                    <i class="bi bi-x-circle me-1"></i>Cancelar
                  </button>
                  <button type="button" class="btn btn-danger" (click)="guardarEdicion()" [disabled]="editar.isPending()">
                    @if (editar.isPending()) {
                      <span class="spinner-border spinner-border-sm me-1"></span>Guardando…
                    } @else {
                      <i class="bi bi-check-circle me-1"></i>Guardar
                    }
                  </button>
                </div>
              </div>
            </div>
          </div>
        }
      </div>
    }
  `,
})
export class DocumentosAsesorComponent {
  readonly numeroDocumento = input.required<string>();

  protected readonly estados = ESTADOS_DOCUMENTO;
  protected readonly leer = leerInput;
  protected readonly docs = injectDocumentosAsesor(
    () => this.numeroDocumento(),
    () => true,
  );
  protected readonly editar = injectEditarDocumento(() => this.numeroDocumento());
  protected readonly editId = signal<number | null>(null);
  protected readonly edit = signal<DocumentoEditState | null>(null);
  protected readonly errorMsg = signal<string>('');

  protected badgeBg(estado: string): string {
    return estadoBadgeBg(estado);
  }

  protected label(estado: string): string {
    return estadoLabel(estado);
  }

  protected fechaDisplay(value: string | null): string {
    return formatFechaDisplay(value);
  }

  protected version(did: number): number {
    return this.docs.data()?.find((d) => d.did === did)?.version ?? 1;
  }

  protected patch(cambios: Partial<DocumentoEditState>): void {
    this.edit.update((prev) => (prev ? { ...prev, ...cambios } : prev));
  }

  protected abrirEdicion(d: DocumentoItem): void {
    this.editId.set(d.did);
    this.edit.set({
      did: d.did,
      nombre: d.nombre,
      estado: (d.estado || 'pendiente').toLowerCase(),
      fecha: formatFechaInput(d.fecha),
    });
    this.errorMsg.set('');
  }

  protected cancelarEdicion(): void {
    this.editId.set(null);
    this.edit.set(null);
    this.errorMsg.set('');
  }

  protected async guardarEdicion(): Promise<void> {
    const edit = this.edit();
    if (!edit) return;
    this.errorMsg.set('');
    const payload: DocumentoEditPayload = {
      nombre: edit.nombre,
      estado: edit.estado,
      fecha: edit.fecha ? new Date(edit.fecha).toISOString() : null,
    };
    try {
      await this.editar.mutateAsync({ did: edit.did, payload });
      this.cancelarEdicion();
    } catch (err) {
      this.errorMsg.set(err instanceof Error ? err.message : 'Error al guardar');
    }
  }
}
