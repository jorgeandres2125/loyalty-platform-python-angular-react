import { ChangeDetectionStrategy, Component, computed, effect, signal } from '@angular/core';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { EstadoSwitchComponent } from '../../shared/ui/components/estado-switch.component';
import { leerInput, mayusculas, soloDigitos } from '../../shared/lib/inputs';
import {
  injectActualizarEjecutivo,
  injectCrearEjecutivo,
  injectEjecutivos,
} from '../../features/ejecutivos/model/queries';
import type { EjecutivoFormPayload, EjecutivoListItem } from '../../features/ejecutivos/model/types';

type Tab = 'lista' | 'registro';

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

const TIPOS_DOCUMENTO: ReadonlyArray<{ value: string; label: string }> = [
  { value: 'CC', label: 'C.C.' },
  { value: 'CE', label: 'C.E.' },
  { value: 'F&I', label: 'F&I' },
  { value: 'GC', label: 'GC' },
  { value: 'PEP', label: 'PEP' },
  { value: 'PPT', label: 'PPT' },
  { value: 'VDA', label: 'VDA' },
];

const PERFILES: ReadonlyArray<{ value: string; label: string }> = [
  { value: '0', label: 'Ejecutivo Consumo' },
  { value: '1', label: 'Ejecutivo Vehiculo' },
  { value: '2', label: 'Ejecutivo Movilidad. Consumo y Servicios' },
];

const PERFIL_BADGE_BG: Record<string, string> = {
  '0': 'info',
  '1': 'primary',
  '2': 'dark',
};

interface FormState {
  tipo_documento: string;
  numero_documento: string;
  nombre_completo: string;
  codigo_ejecutivo: string;
  email: string;
  celular: string;
  perfil: string;
  estado: boolean;
}

const initForm: FormState = {
  tipo_documento: 'CC',
  numero_documento: '',
  nombre_completo: '',
  codigo_ejecutivo: '',
  email: '',
  celular: '',
  perfil: '0',
  estado: true,
};

@Component({
  selector: 'app-ejecutivos-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, EstadoSwitchComponent],
  template: `
    <div>
      <app-page-header title="Ejecutivos" [subtitle]="subtitulo()" icon="bi-person-workspace" />

      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white border-bottom-0 pb-0">
          <ul class="nav nav-tabs">
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'lista'" (click)="tab.set('lista')">
                <i class="bi bi-list-ul me-2"></i>Lista de Ejecutivos
              </button>
            </li>
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'registro'" (click)="tab.set('registro')">
                <i class="bi me-2" [class]="isEditing() ? 'bi-pencil-square' : 'bi-person-plus'"></i>
                {{ isEditing() ? 'Editar Ejecutivo' : 'Nuevo Ejecutivo' }}
              </button>
            </li>
          </ul>
        </div>
        <div class="card-body" [class]="tab() === 'lista' ? 'p-0' : 'p-4'">
          @if (tab() === 'lista') {
            <!-- ── Lista ── -->
            @if (success()) {
              <div class="px-3 pt-3">
                <div class="alert alert-success alert-dismissible mb-0">
                  <i class="bi bi-check-circle me-2"></i>
                  {{ success() }}
                  <button type="button" class="btn-close" aria-label="Close" (click)="success.set('')"></button>
                </div>
              </div>
            }
            <div class="d-flex align-items-center justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
              <small class="text-muted">{{ conteo() }}</small>
              <div class="d-flex align-items-center gap-2">
                <select class="form-select form-select-sm" style="width: auto"
                  (change)="setPageSize(+$any($event.target).value)">
                  @for (size of pageSizeOptions; track size) {
                    <option [value]="size" [selected]="size === pageSize()">Ver {{ size }} por página</option>
                  }
                </select>
                <button type="button" class="btn btn-danger btn-sm" (click)="handleNuevo()">
                  <i class="bi bi-person-plus me-1"></i>Nuevo Ejecutivo
                </button>
              </div>
            </div>

            <div class="px-3 pb-3">
              <div class="d-flex align-items-end gap-2 flex-wrap p-3 rounded"
                style="background: #f8f9fa; border: 1px solid #dee2e6">
                <div style="min-width: 160px">
                  <label class="form-label small mb-1 fw-semibold">Tipo de Documento</label>
                  <select class="form-select form-select-sm" (change)="searchTipoDoc.set($any($event.target).value)">
                    <option value="" [selected]="searchTipoDoc() === ''">Todos</option>
                    @for (t of tiposDocumento; track t.value) {
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
            } @else if (lista.isError()) {
              <div class="alert alert-danger mx-3">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Error al cargar los ejecutivos.
              </div>
            } @else if (!lista.data() || lista.data()!.items.length === 0) {
              <div class="text-center py-5 text-muted">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                Sin ejecutivos registrados
              </div>
            } @else {
              <div class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Tipo Doc.</th>
                      <th>Número Documento</th>
                      <th>Nombre y Apellidos</th>
                      <th>Código Ejecutivo</th>
                      <th>Correo Electrónico</th>
                      <th>Celular</th>
                      <th class="text-center">Estado</th>
                      <th>Perfil</th>
                      <th class="text-center">Operación</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (item of lista.data()!.items; track item.id) {
                      <tr>
                        <td>{{ item.tipo_documento || '—' }}</td>
                        <td class="font-monospace">{{ item.numero_documento }}</td>
                        <td>{{ item.nombre_completo || '—' }}</td>
                        <td class="font-monospace">{{ item.codigo_ejecutivo || '—' }}</td>
                        <td>{{ item.email || '—' }}</td>
                        <td class="font-monospace">{{ item.celular || '—' }}</td>
                        <td class="text-center">
                          <span class="badge" [class]="item.estado ? 'bg-success' : 'bg-secondary'">
                            {{ item.estado ? 'Activo' : 'Inactivo' }}
                          </span>
                        </td>
                        <td>
                          <span class="badge" [class]="'bg-' + perfilBadge(item.perfil)">{{ item.perfil_nombre || '—' }}</span>
                        </td>
                        <td class="text-center">
                          <button type="button" class="btn btn-outline-primary btn-sm" (click)="handleEditar(item)">
                            <i class="bi bi-pencil me-1"></i>Editar
                          </button>
                        </td>
                      </tr>
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
          } @else {
            <!-- ── Formulario ── -->
            @let f = form();
            <form (submit)="handleGuardar($event)">
              <h6 class="fw-semibold mb-3">
                <i class="bi me-2 text-danger" [class]="isEditing() ? 'bi-pencil-square' : 'bi-person-plus'"></i>
                {{ isEditing() ? 'Editar Ejecutivo' : 'Nuevo Ejecutivo' }}
              </h6>

              @if (error()) {
                <div class="alert alert-danger alert-dismissible">
                  <i class="bi bi-exclamation-circle me-2"></i>
                  {{ error() }}
                  <button type="button" class="btn-close" aria-label="Close"></button>
                </div>
              }
              @if (success()) {
                <div class="alert alert-success">
                  <i class="bi bi-check-circle me-2"></i>
                  {{ success() }}
                </div>
              }

              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label small fw-semibold mb-1">Tipo de Documento <span class="text-danger">*</span></label>
                  <select class="form-select" required (change)="patch({ tipo_documento: $any($event.target).value })">
                    @for (t of tiposDocumento; track t.value) {
                      <option [value]="t.value" [selected]="t.value === f.tipo_documento">{{ t.label }}</option>
                    }
                  </select>
                </div>

                <div class="col-md-4">
                  <label class="form-label small fw-semibold mb-1">Número de Documento <span class="text-danger">*</span></label>
                  <input class="form-control font-monospace" [value]="f.numero_documento"
                    (input)="patch({ numero_documento: leer($event, soloDigitos) })" placeholder="Ej: 1037585639"
                    maxlength="40" required [disabled]="isEditing()" />
                </div>

                <div class="col-md-4">
                  <label class="form-label small fw-semibold mb-1">Código Ejecutivo <span class="text-danger">*</span></label>
                  <input class="form-control font-monospace" [value]="f.codigo_ejecutivo"
                    (input)="patch({ codigo_ejecutivo: leer($event) })" placeholder="Ej: 12345" maxlength="200" required />
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-semibold mb-1">Nombre y Apellidos <span class="text-danger">*</span></label>
                  <input class="form-control" [value]="f.nombre_completo"
                    (input)="patch({ nombre_completo: leer($event, mayusculas) })" placeholder="Nombre completo"
                    maxlength="200" required />
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-semibold mb-1">Correo Electrónico <span class="text-danger">*</span></label>
                  <input class="form-control" type="email" [value]="f.email" (input)="patch({ email: leer($event) })"
                    placeholder="ejecutivo@sufi.com" maxlength="254" required />
                </div>

                <div class="col-md-4">
                  <label class="form-label small fw-semibold mb-1">Celular</label>
                  <input class="form-control font-monospace" [value]="f.celular"
                    (input)="patch({ celular: leer($event, soloDigitos) })" placeholder="3001234567" maxlength="36" />
                </div>

                <div class="col-md-4">
                  <label class="form-label small fw-semibold mb-1">Perfil <span class="text-danger">*</span></label>
                  <select class="form-select" required (change)="patch({ perfil: $any($event.target).value })">
                    @for (p of perfiles; track p.value) {
                      <option [value]="p.value" [selected]="p.value === f.perfil">{{ p.label }}</option>
                    }
                  </select>
                </div>

                <div class="col-md-4 d-flex align-items-end">
                  <div>
                    <app-estado-switch id="ejecutivo-estado" [checked]="f.estado" (checkedChange)="patch({ estado: $event })" />
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-outline-secondary" (click)="handleCancelar()" [disabled]="isSaving()">
                  <i class="bi bi-x-circle me-1"></i>Cancelar
                </button>
                <button type="submit" class="btn btn-danger" [disabled]="isSaving()">
                  @if (isSaving()) {
                    <span class="spinner-border spinner-border-sm me-1"></span>Guardando…
                  } @else {
                    <i class="bi bi-check-circle me-1"></i>{{ isEditing() ? 'Actualizar' : 'Crear' }} Ejecutivo
                  }
                </button>
              </div>
            </form>
          }
        </div>
      </div>
    </div>
  `,
})
export class EjecutivosPageComponent {
  protected readonly pageSizeOptions = PAGE_SIZE_OPTIONS;
  protected readonly tiposDocumento = TIPOS_DOCUMENTO;
  protected readonly perfiles = PERFILES;
  protected readonly leer = leerInput;
  protected readonly soloDigitos = soloDigitos;
  protected readonly mayusculas = mayusculas;

  protected readonly tab = signal<Tab>('lista');
  protected readonly page = signal<number>(1);
  protected readonly pageSize = signal<number>(10);
  protected readonly searchTipoDoc = signal<string>('');
  protected readonly searchDocumento = signal<string>('');
  private readonly filtroTipoDoc = signal<string>('');
  private readonly filtroDocumento = signal<string>('');

  protected readonly editId = signal<number | null>(null);
  protected readonly form = signal<FormState>(initForm);
  protected readonly error = signal<string>('');
  protected readonly success = signal<string>('');

  protected readonly lista = injectEjecutivos(() => ({
    page: this.page(),
    page_size: this.pageSize(),
    tipo_doc: this.filtroTipoDoc() || undefined,
    documento: this.filtroDocumento() || undefined,
  }));
  private readonly crearMut = injectCrearEjecutivo();
  private readonly actualizarMut = injectActualizarEjecutivo();

  private readonly filtrosActivos = computed<boolean>(() => !!this.filtroTipoDoc() || !!this.filtroDocumento());
  protected readonly totalPages = computed<number>(() => {
    const data = this.lista.data();
    return data ? Math.max(1, Math.ceil(data.total / this.pageSize())) : 1;
  });
  protected readonly isEditing = computed<boolean>(() => this.editId() !== null);
  protected readonly isSaving = computed<boolean>(() => this.crearMut.isPending() || this.actualizarMut.isPending());

  protected readonly subtitulo = computed<string | undefined>(() => {
    const data = this.lista.data();
    return data ? `${data.total} ejecutivos${this.filtrosActivos() ? ' encontrados' : ''}` : undefined;
  });
  protected readonly conteo = computed<string>(() => {
    const data = this.lista.data();
    if (!data) return '';
    return `${data.total} ejecutivo${data.total === 1 ? '' : 's'}${this.filtrosActivos() ? ' encontrados' : ''}`;
  });

  constructor() {
    effect(() => {
      if (this.tab() !== 'registro') this.error.set('');
    });
    effect((onCleanup) => {
      if (!this.success()) return;
      const timeoutId = setTimeout(() => this.success.set(''), 3500);
      onCleanup(() => clearTimeout(timeoutId));
    });
  }

  protected perfilBadge(perfil: string): string {
    return PERFIL_BADGE_BG[perfil] ?? 'secondary';
  }

  protected patch(cambios: Partial<FormState>): void {
    this.form.update((prev) => ({ ...prev, ...cambios }));
  }

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

  protected handleNuevo(): void {
    this.editId.set(null);
    this.form.set(initForm);
    this.error.set('');
    this.success.set('');
    this.tab.set('registro');
  }

  protected handleEditar(item: EjecutivoListItem): void {
    this.editId.set(item.id);
    this.form.set({
      tipo_documento: item.tipo_documento || 'CC',
      numero_documento: item.numero_documento,
      nombre_completo: item.nombre_completo,
      codigo_ejecutivo: item.codigo_ejecutivo,
      email: item.email,
      celular: item.celular,
      perfil: item.perfil || '0',
      estado: item.estado,
    });
    this.error.set('');
    this.success.set('');
    this.tab.set('registro');
  }

  protected handleCancelar(): void {
    this.editId.set(null);
    this.form.set(initForm);
    this.error.set('');
    this.success.set('');
    this.tab.set('lista');
  }

  protected async handleGuardar(e: Event): Promise<void> {
    e.preventDefault();
    this.error.set('');
    this.success.set('');
    const form: FormState = this.form();

    if (
      !form.tipo_documento ||
      !form.numero_documento.trim() ||
      !form.nombre_completo.trim() ||
      !form.codigo_ejecutivo.trim() ||
      !form.email.trim() ||
      !form.perfil
    ) {
      this.error.set('Completa todos los campos obligatorios (marcados con *)');
      return;
    }

    const payload: EjecutivoFormPayload = {
      tipo_documento: form.tipo_documento,
      numero_documento: form.numero_documento.trim(),
      nombre_completo: form.nombre_completo.trim(),
      codigo_ejecutivo: form.codigo_ejecutivo.trim(),
      email: form.email.trim(),
      celular: form.celular.trim(),
      perfil: form.perfil,
      estado: form.estado,
    };

    try {
      const editId = this.editId();
      if (editId !== null) {
        await this.actualizarMut.mutateAsync({ id: editId, payload });
        this.success.set('Ejecutivo actualizado correctamente');
      } else {
        await this.crearMut.mutateAsync(payload);
        this.success.set('Ejecutivo creado correctamente');
      }
      this.editId.set(null);
      this.form.set(initForm);
      this.tab.set('lista');
    } catch (err) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      const msg: string = Array.isArray(detail)
        ? detail.join('; ')
        : typeof detail === 'string'
          ? detail
          : err instanceof Error
            ? err.message
            : 'Error al guardar';
      this.error.set(msg);
    }
  }
}
