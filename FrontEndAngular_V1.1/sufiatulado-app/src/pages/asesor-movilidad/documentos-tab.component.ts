import { ChangeDetectionStrategy, Component, computed, signal } from '@angular/core';
import { injectAsesoresConDocumentos } from '../../features/documentos/model/queries';
import { leerInput, soloDigitos } from '../../shared/lib/inputs';
import { DocumentosAsesorComponent } from './documentos-asesor.component';

const PROGRAMA_MOVILIDAD_ID = 1 as const;
const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];
const TIPOS_DOC: ReadonlyArray<{ value: string; label: string }> = [
  { value: 'CC', label: 'C.C.' },
  { value: 'CE', label: 'C.E.' },
  { value: 'F&I', label: 'F&I' },
  { value: 'GC', label: 'GC' },
  { value: 'PEP', label: 'PEP' },
  { value: 'PPT', label: 'PPT' },
  { value: 'VDA', label: 'VDA' },
];

@Component({
  selector: 'app-documentos-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [DocumentosAsesorComponent],
  template: `
    <div class="d-flex align-items-center justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
      <small class="text-muted">
        @if (lista.data(); as data) {
          {{ data.total }} {{ filtrosActivos() ? 'asesores encontrados' : 'asesores con documentos' }}
        }
      </small>
      <select class="form-select form-select-sm" style="width: auto" (change)="setPageSize(+$any($event.target).value)">
        @for (size of pageSizeOptions; track size) {
          <option [value]="size" [selected]="size === pageSize()">Ver {{ size }} por página</option>
        }
      </select>
    </div>

    <div class="px-3 pb-3">
      <div class="d-flex align-items-end gap-2 flex-wrap p-3 rounded" style="background: #f8f9fa; border: 1px solid #dee2e6">
        <div style="min-width: 160px">
          <label class="form-label small mb-1 fw-semibold">Tipo de Documento</label>
          <select class="form-select form-select-sm" (change)="searchTipoDoc.set($any($event.target).value)">
            <option value="" [selected]="searchTipoDoc() === ''">Todos</option>
            @for (t of tiposDoc; track t.value) {
              <option [value]="t.value" [selected]="t.value === searchTipoDoc()">{{ t.label }}</option>
            }
          </select>
        </div>
        <div style="min-width: 180px">
          <label class="form-label small mb-1 fw-semibold">Documento</label>
          <input class="form-control form-control-sm" placeholder="Ej: 12345678" [value]="searchDocumento()"
            (input)="searchDocumento.set(leer($event, soloDigitos))" maxlength="20" />
        </div>
        <button type="button" class="btn btn-danger btn-sm" [disabled]="!searchTipoDoc() && !searchDocumento()"
          (click)="handleBuscar()">
          <i class="bi bi-search me-1"></i>Buscar
        </button>
        <button type="button" class="btn btn-outline-secondary btn-sm" (click)="handleLimpiar()">
          <i class="bi bi-x-circle me-1"></i>Limpiar
        </button>
      </div>
    </div>

    @if (lista.isLoading()) {
      <div class="text-center py-5"><div class="spinner-border text-danger" role="status"></div></div>
    } @else if (!lista.data() || lista.data()!.items.length === 0) {
      <div class="text-center py-5 text-muted">
        <i class="bi bi-inbox fs-1 d-block mb-2"></i>
        Sin asesores con documentos
      </div>
    } @else {
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Tipo de Documento</th>
              <th>Usuario</th>
              <th>Email</th>
              <th class="text-center">Operación</th>
            </tr>
          </thead>
          <tbody>
            @for (item of lista.data()!.items; track item.numero_documento) {
              @let abierto = expandido() === item.numero_documento;
              <tr>
                <td>{{ item.tipo_documento }}</td>
                <td class="font-monospace">{{ item.numero_documento }}</td>
                <td>{{ item.email ?? '—' }}</td>
                <td class="text-center">
                  <button type="button" class="btn btn-sm" [class]="abierto ? 'btn-secondary' : 'btn-outline-danger'"
                    (click)="expandido.set(abierto ? null : item.numero_documento)">
                    <i class="bi me-1" [class]="abierto ? 'bi-chevron-up' : 'bi-folder2-open'"></i>
                    {{ abierto ? 'Cerrar' : 'Ver Documentación' }}
                  </button>
                </td>
              </tr>
              @if (abierto) {
                <tr>
                  <td colspan="4" class="p-0">
                    <app-documentos-asesor [numeroDocumento]="item.numero_documento" />
                  </td>
                </tr>
              }
            }
          </tbody>
        </table>
      </div>
    }

    @if (lista.data() && totalPages() > 1) {
      <div class="d-flex justify-content-center align-items-center gap-2 py-3">
        <button type="button" class="btn btn-outline-secondary btn-sm" [disabled]="page() === 1" (click)="page.set(1)">
          <i class="bi bi-chevron-double-left"></i>
        </button>
        <button type="button" class="btn btn-outline-secondary btn-sm" [disabled]="page() === 1" (click)="page.set(page() - 1)">
          <i class="bi bi-chevron-left"></i>
        </button>
        <span class="small">Página {{ page() }} de {{ totalPages() }}</span>
        <button type="button" class="btn btn-outline-secondary btn-sm" [disabled]="page() === totalPages()"
          (click)="page.set(page() + 1)">
          <i class="bi bi-chevron-right"></i>
        </button>
        <button type="button" class="btn btn-outline-secondary btn-sm" [disabled]="page() === totalPages()"
          (click)="page.set(totalPages())">
          <i class="bi bi-chevron-double-right"></i>
        </button>
      </div>
    }
  `,
})
export class DocumentosTabComponent {
  protected readonly pageSizeOptions = PAGE_SIZE_OPTIONS;
  protected readonly tiposDoc = TIPOS_DOC;
  protected readonly leer = leerInput;
  protected readonly soloDigitos = soloDigitos;

  protected readonly page = signal<number>(1);
  protected readonly pageSize = signal<number>(10);
  protected readonly searchTipoDoc = signal<string>('');
  protected readonly searchDocumento = signal<string>('');
  private readonly filtroTipoDoc = signal<string>('');
  private readonly filtroDocumento = signal<string>('');
  protected readonly expandido = signal<string | null>(null);

  protected readonly filtrosActivos = computed<boolean>(() => !!this.filtroTipoDoc() || !!this.filtroDocumento());

  protected readonly lista = injectAsesoresConDocumentos(() => ({
    programa: PROGRAMA_MOVILIDAD_ID,
    page: this.page(),
    page_size: this.pageSize(),
    cedula: this.filtroDocumento() || undefined,
    tipo_doc: this.filtroTipoDoc() || undefined,
  }));

  protected readonly totalPages = computed<number>(() => {
    const data = this.lista.data();
    return data ? Math.max(1, Math.ceil(data.total / this.pageSize())) : 1;
  });

  protected setPageSize(n: number): void {
    this.pageSize.set(n);
    this.page.set(1);
  }

  protected handleBuscar(): void {
    this.filtroTipoDoc.set(this.searchTipoDoc());
    this.filtroDocumento.set(this.searchDocumento().trim());
    this.page.set(1);
  }

  protected handleLimpiar(): void {
    this.searchTipoDoc.set('');
    this.searchDocumento.set('');
    this.filtroTipoDoc.set('');
    this.filtroDocumento.set('');
    this.page.set(1);
  }
}
