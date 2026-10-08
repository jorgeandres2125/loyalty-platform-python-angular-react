import { ChangeDetectionStrategy, Component, computed, effect, signal, untracked } from '@angular/core';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import {
  TomSelectFieldComponent,
  type TomSelectOption,
} from '../../shared/ui/components/tom-select-field.component';
import { TomSelectMultiFieldComponent } from '../../shared/ui/components/tom-select-multi-field.component';
import { EstadoSwitchComponent } from '../../shared/ui/components/estado-switch.component';
import { leerInput } from '../../shared/lib/inputs';
import {
  injectActualizarOficina,
  injectCrearOficina,
  injectOficina,
  injectOficinas,
} from '../../features/oficinas/model/queries';
import type { OficinaFormPayload, OficinaListItem } from '../../features/oficinas/model/types';
import { injectCanalesActivas } from '../../features/canales/model/queries';
import { injectCiudades, injectDepartamentos } from '../../features/ubicaciones/model/ubicaciones';

type Tab = 'lista' | 'registro';

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

const ESTADO_OPTIONS: ReadonlyArray<{ value: string; label: string }> = [
  { value: '', label: 'Todos' },
  { value: 'true', label: 'Activos' },
  { value: 'false', label: 'Inactivos' },
];

interface FormState {
  cod_oficinas: string;
  id_oficinas: string;
  nom_oficinas: string;
  marca: string;
  regional: string;
  did: string; // departamentos.did — solo para filtrar ciudades
  cpid: string; // ciudades.cid — se persiste en oficinas.cpid
  ind_activo: boolean;
  canales_ids: string[];
}

const initForm: FormState = {
  cod_oficinas: '',
  id_oficinas: '',
  nom_oficinas: '',
  marca: '',
  regional: '',
  did: '',
  cpid: '',
  ind_activo: true,
  canales_ids: [],
};

@Component({
  selector: 'app-oficinas-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, TomSelectFieldComponent, TomSelectMultiFieldComponent, EstadoSwitchComponent],
  template: `
    <div>
      <app-page-header title="Oficinas" [subtitle]="subtitulo()" icon="bi-building" />

      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white border-bottom-0 pb-0">
          <ul class="nav nav-tabs">
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'lista'" (click)="tab.set('lista')">
                <i class="bi bi-list-ul me-2"></i>Lista de Oficinas
              </button>
            </li>
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'registro'" (click)="tab.set('registro')">
                <i class="bi me-2" [class]="isEditing() ? 'bi-pencil-square' : 'bi-plus-circle'"></i>
                {{ isEditing() ? 'Editar Oficina' : 'Nueva Oficina' }}
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
            <div class="d-flex align-items-end justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
              <div class="d-flex align-items-end gap-2 flex-wrap">
                <div style="min-width: 180px">
                  <label class="form-label small mb-1">Nombre</label>
                  <input class="form-control form-control-sm" type="text" placeholder="Filtrar por nombre..."
                    [value]="searchNombre()" (input)="searchNombre.set(leer($event))" (keydown.enter)="handleBuscar()"
                    maxlength="120" />
                </div>
                <div style="min-width: 130px">
                  <label class="form-label small mb-1">Marca</label>
                  <input class="form-control form-control-sm" type="text" placeholder="Marca..."
                    [value]="searchMarca()" (input)="searchMarca.set(leer($event))" (keydown.enter)="handleBuscar()"
                    maxlength="45" />
                </div>
                <div style="min-width: 130px">
                  <label class="form-label small mb-1">Regional</label>
                  <input class="form-control form-control-sm" type="text" placeholder="Regional..."
                    [value]="searchRegional()" (input)="searchRegional.set(leer($event))" (keydown.enter)="handleBuscar()"
                    maxlength="45" />
                </div>
                <div style="min-width: 130px">
                  <label class="form-label small mb-1">Estado</label>
                  <select class="form-select form-select-sm" (change)="searchEstado.set($any($event.target).value)">
                    @for (opt of estadoOptions; track opt.value) {
                      <option [value]="opt.value" [selected]="opt.value === searchEstado()">{{ opt.label }}</option>
                    }
                  </select>
                </div>
                <button type="button" class="btn btn-sm btn-primary" (click)="handleBuscar()">
                  <i class="bi bi-search me-1"></i>Buscar
                </button>
                @if (filtrosActivos()) {
                  <button type="button" class="btn btn-sm btn-outline-secondary" (click)="handleLimpiar()">
                    <i class="bi bi-x-circle me-1"></i>Limpiar
                  </button>
                }
              </div>
              <div class="d-flex align-items-end gap-2">
                <div style="min-width: 80px">
                  <label class="form-label small mb-1">Mostrar</label>
                  <select class="form-select form-select-sm" (change)="setPageSize(+$any($event.target).value)">
                    @for (size of pageSizeOptions; track size) {
                      <option [value]="size" [selected]="size === pageSize()">{{ size }}</option>
                    }
                  </select>
                </div>
                <button type="button" class="btn btn-sm btn-success" (click)="handleNuevo()">
                  <i class="bi bi-plus-lg me-1"></i>Nueva Oficina
                </button>
              </div>
            </div>

            @if (lista.isLoading()) {
              <div class="text-center py-5"><div class="spinner-border" role="status"></div></div>
            } @else if (lista.isError()) {
              <div class="alert alert-danger m-3">Error al cargar oficinas</div>
            } @else if (!lista.data() || lista.data()!.items.length === 0) {
              <div class="text-center py-5 text-muted">
                <i class="bi bi-inbox display-4 d-block mb-2"></i>
                No se encontraron oficinas
              </div>
            } @else {
              <div class="table-responsive">
                <table class="table table-hover mb-0 align-middle">
                  <thead class="table-light">
                    <tr>
                      <th>Código</th>
                      <th>Nombre</th>
                      <th>Marca</th>
                      <th>Regional</th>
                      <th>Ciudad</th>
                      <th>Departamento</th>
                      <th>Estado</th>
                      <th class="text-end">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (oficina of lista.data()!.items; track oficina.cod_oficinas) {
                      <tr>
                        <td><code>{{ oficina.cod_oficinas }}</code></td>
                        <td class="fw-semibold">{{ oficina.nom_oficinas }}</td>
                        <td>@if (oficina.marca) { {{ oficina.marca }} } @else { <span class="text-muted">—</span> }</td>
                        <td>@if (oficina.regional) { {{ oficina.regional }} } @else { <span class="text-muted">—</span> }</td>
                        <td>
                          @if (oficina.ciudad_nombre) { {{ oficina.ciudad_nombre }} } @else { <span class="text-muted">—</span> }
                        </td>
                        <td>
                          @if (oficina.departamento_nombre) {
                            {{ oficina.departamento_nombre }}
                          } @else {
                            <span class="text-muted">—</span>
                          }
                        </td>
                        <td>
                          <span class="badge" [class]="oficina.ind_activo ? 'bg-success' : 'bg-secondary'">
                            {{ oficina.ind_activo ? 'Activa' : 'Inactiva' }}
                          </span>
                        </td>
                        <td class="text-end">
                          <button type="button" class="btn btn-sm btn-outline-primary" (click)="handleEditar(oficina)">
                            <i class="bi bi-pencil-square me-1"></i>Editar
                          </button>
                        </td>
                      </tr>
                    }
                  </tbody>
                </table>
              </div>
              <div class="d-flex align-items-center justify-content-between px-3 py-2 border-top">
                <small class="text-muted">
                  Página {{ page() }} de {{ totalPages() }} · {{ lista.data()!.total }} registros
                </small>
                <div class="d-flex gap-1">
                  <button type="button" class="btn btn-sm btn-outline-secondary" [disabled]="page() <= 1" (click)="page.set(1)">
                    <i class="bi bi-chevron-double-left"></i>
                  </button>
                  <button type="button" class="btn btn-sm btn-outline-secondary" [disabled]="page() <= 1" (click)="page.set(page() - 1)">
                    <i class="bi bi-chevron-left"></i>
                  </button>
                  <button type="button" class="btn btn-sm btn-outline-secondary" [disabled]="page() >= totalPages()"
                    (click)="page.set(page() + 1)">
                    <i class="bi bi-chevron-right"></i>
                  </button>
                  <button type="button" class="btn btn-sm btn-outline-secondary" [disabled]="page() >= totalPages()"
                    (click)="page.set(totalPages())">
                    <i class="bi bi-chevron-double-right"></i>
                  </button>
                </div>
              </div>
            }
          } @else {
            <!-- ── Formulario ── -->
            @let f = form();
            <form (submit)="handleGuardar($event)">
              @if (error()) {
                <div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>{{ error() }}</div>
              }
              @if (success()) {
                <div class="alert alert-success"><i class="bi bi-check-circle me-2"></i>{{ success() }}</div>
              }

              <div class="row g-3">
                <!-- Identificadores del sistema — solo visibles en edición -->
                @if (isEditing()) {
                  <div class="col-md-4">
                    <label class="form-label text-muted small">Código de oficina</label>
                    <input type="text" class="form-control-plaintext fw-semibold" [value]="f.cod_oficinas" readonly />
                  </div>
                  <div class="col-md-8"></div>
                }

                <div class="col-md-4">
                  <label class="form-label">Nombre de la oficina <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" [value]="f.nom_oficinas" (input)="patch({ nom_oficinas: leer($event) })"
                    placeholder="Ej. AUTOMONTANA - BOGOTA" maxlength="120" required />
                </div>

                <div class="col-md-4">
                  <label class="form-label">Marca</label>
                  <input type="text" class="form-control" [value]="f.marca" (input)="patch({ marca: leer($event) })"
                    placeholder="Ej. RENAULT, MAZDA, KIA..." maxlength="45" />
                </div>

                <div class="col-md-4">
                  <label class="form-label">Regional</label>
                  <input type="text" class="form-control" [value]="f.regional" (input)="patch({ regional: leer($event) })"
                    placeholder="Ej. BOGOTA, SUR, CARIBE..." maxlength="45" />
                </div>

                <!-- Departamento -->
                <div class="col-md-4">
                  <label class="form-label" for="oficina-departamento">Departamento <span class="text-danger">*</span></label>
                  <app-tom-select-field
                    id="oficina-departamento"
                    [options]="depOpts()"
                    [value]="f.did"
                    (valueChange)="handleDepartamentoChange($event)"
                    placeholder="— Seleccionar departamento —"
                    [required]="true"
                  />
                </div>

                <!-- Ciudad (se recrea al cambiar de departamento) -->
                <div class="col-md-4">
                  <label class="form-label" for="oficina-ciudad">
                    Ciudad <span class="text-danger">*</span>
                    @if (ciudadesQ.isFetching()) {
                      <span class="spinner-border spinner-border-sm ms-2"></span>
                    }
                  </label>
                  @for (k of [f.did]; track k) {
                    <app-tom-select-field
                      id="oficina-ciudad"
                      [options]="ciudadOpts()"
                      [value]="f.cpid"
                      (valueChange)="patch({ cpid: $event })"
                      [placeholder]="f.did ? '— Seleccionar ciudad —' : '— Selecciona primero un departamento —'"
                      [disabled]="!f.did || ciudadesQ.isFetching()"
                      [required]="true"
                    />
                  }
                  @if (!f.did) {
                    <div class="form-text text-muted">Selecciona un departamento para ver las ciudades.</div>
                  }
                </div>

                <!-- Estado -->
                <div class="col-md-4 d-flex align-items-end">
                  <app-estado-switch
                    id="oficina-estado"
                    [checked]="f.ind_activo"
                    (checkedChange)="patch({ ind_activo: $event })"
                    labelActivo="Activa"
                    labelInactivo="Inactiva"
                  />
                </div>

                <div class="col-12">
                  <label class="form-label" for="oficina-canales">
                    Canales asociados
                    @if (canalesActivasQ.isLoading()) {
                      <span class="spinner-border spinner-border-sm ms-2"></span>
                    }
                  </label>
                  <app-tom-select-multi-field
                    id="oficina-canales"
                    [options]="canalOpts()"
                    [value]="f.canales_ids"
                    (valueChange)="patch({ canales_ids: $event })"
                    placeholder="— Seleccionar uno o varios canales —"
                    [disabled]="canalesActivasQ.isLoading()"
                  />
                  <div class="form-text text-muted">{{ ayudaCanales() }}</div>
                </div>
              </div>

              <div class="d-flex gap-2 mt-4 pt-3 border-top">
                <button type="submit" class="btn btn-primary" [disabled]="isSaving()">
                  @if (isSaving()) {
                    <span class="spinner-border spinner-border-sm me-2"></span>Guardando...
                  } @else {
                    <i class="bi bi-check-lg me-1"></i>{{ isEditing() ? 'Actualizar' : 'Crear' }}
                  }
                </button>
                <button type="button" class="btn btn-outline-secondary" (click)="handleCancelar()" [disabled]="isSaving()">
                  <i class="bi bi-x-lg me-1"></i>Cancelar
                </button>
              </div>
            </form>
          }
        </div>
      </div>
    </div>
  `,
})
export class OficinasPageComponent {
  protected readonly pageSizeOptions = PAGE_SIZE_OPTIONS;
  protected readonly estadoOptions = ESTADO_OPTIONS;
  protected readonly leer = leerInput;

  protected readonly tab = signal<Tab>('lista');
  protected readonly page = signal<number>(1);
  protected readonly pageSize = signal<number>(10);
  protected readonly searchNombre = signal<string>('');
  protected readonly searchMarca = signal<string>('');
  protected readonly searchRegional = signal<string>('');
  protected readonly searchEstado = signal<string>('');
  private readonly filtroNombre = signal<string>('');
  private readonly filtroMarca = signal<string>('');
  private readonly filtroRegional = signal<string>('');
  private readonly filtroEstado = signal<string>('');

  protected readonly editId = signal<number | null>(null);
  protected readonly form = signal<FormState>(initForm);
  protected readonly error = signal<string>('');
  protected readonly success = signal<string>('');

  protected readonly lista = injectOficinas(() => {
    const estado: string = this.filtroEstado();
    return {
      page: this.page(),
      page_size: this.pageSize(),
      nombre: this.filtroNombre() || undefined,
      marca: this.filtroMarca() || undefined,
      regional: this.filtroRegional() || undefined,
      ind_activo: estado === '' ? undefined : estado === 'true',
    };
  });

  private readonly departamentosQ = injectDepartamentos();
  protected readonly ciudadesQ = injectCiudades(() => {
    const did: string = this.form().did;
    return did ? parseInt(did, 10) : null;
  });
  protected readonly canalesActivasQ = injectCanalesActivas();
  private readonly oficinaEditQ = injectOficina(() => this.editId());
  private readonly crearMut = injectCrearOficina();
  private readonly actualizarMut = injectActualizarOficina();

  protected readonly filtrosActivos = computed<boolean>(
    () => !!this.filtroNombre() || !!this.filtroMarca() || !!this.filtroRegional() || this.filtroEstado() !== '',
  );
  protected readonly totalPages = computed<number>(() => {
    const data = this.lista.data();
    return data ? Math.max(1, Math.ceil(data.total / this.pageSize())) : 1;
  });
  protected readonly subtitulo = computed<string | undefined>(() => {
    const total: number | undefined = this.lista.data()?.total;
    if (total === undefined) return undefined;
    return `${total} oficinas${this.filtrosActivos() ? ' encontradas' : ''}`;
  });
  protected readonly isEditing = computed<boolean>(() => this.editId() !== null);
  protected readonly isSaving = computed<boolean>(() => this.crearMut.isPending() || this.actualizarMut.isPending());

  protected readonly depOpts = computed<TomSelectOption[]>(() =>
    (this.departamentosQ.data() ?? []).map((dep) => ({ value: String(dep.did), label: dep.departamento })),
  );
  protected readonly ciudadOpts = computed<TomSelectOption[]>(() =>
    (this.ciudadesQ.data() ?? []).map((c) => ({ value: String(c.cid), label: c.ciudad })),
  );
  protected readonly canalOpts = computed<TomSelectOption[]>(() =>
    (this.canalesActivasQ.data() ?? []).map((c) => ({ value: String(c.cod_canales), label: c.nom_canales })),
  );
  protected readonly ayudaCanales = computed<string>(() => {
    const n: number = this.form().canales_ids.length;
    if (n === 0) return 'Una oficina puede asociarse a varios canales.';
    return `${n} canal${n === 1 ? '' : 'es'} seleccionado${n === 1 ? '' : 's'}.`;
  });

  constructor() {
    // Cuando se está editando y llega el detalle de la oficina, sincroniza canales_ids.
    effect(() => {
      const editId = this.editId();
      const data = this.oficinaEditQ.data();
      if (!editId || !data || data.cod_oficinas !== editId) return;
      untracked(() => this.patch({ canales_ids: data.canales_ids.map((id) => String(id)) }));
    });
    effect(() => {
      if (this.tab() !== 'registro') this.error.set('');
    });
    effect((onCleanup) => {
      if (!this.success()) return;
      const timeoutId = setTimeout(() => this.success.set(''), 3500);
      onCleanup(() => clearTimeout(timeoutId));
    });
  }

  protected patch(cambios: Partial<FormState>): void {
    this.form.update((prev) => ({ ...prev, ...cambios }));
  }

  protected setPageSize(n: number): void {
    this.pageSize.set(n);
    this.page.set(1);
  }

  protected handleDepartamentoChange(value: string): void {
    if (value === this.form().did) return;
    this.patch({ did: value, cpid: '' });
  }

  protected handleBuscar(): void {
    this.filtroNombre.set(this.searchNombre().trim());
    this.filtroMarca.set(this.searchMarca().trim());
    this.filtroRegional.set(this.searchRegional().trim());
    this.filtroEstado.set(this.searchEstado());
    this.page.set(1);
  }

  protected handleLimpiar(): void {
    this.searchNombre.set('');
    this.searchMarca.set('');
    this.searchRegional.set('');
    this.searchEstado.set('');
    this.filtroNombre.set('');
    this.filtroMarca.set('');
    this.filtroRegional.set('');
    this.filtroEstado.set('');
    this.page.set(1);
  }

  protected handleNuevo(): void {
    this.editId.set(null);
    this.form.set(initForm);
    this.error.set('');
    this.success.set('');
    this.tab.set('registro');
  }

  protected handleEditar(item: OficinaListItem): void {
    this.editId.set(item.cod_oficinas);
    this.form.set({
      cod_oficinas: String(item.cod_oficinas),
      id_oficinas: item.id_oficinas === null ? '' : String(item.id_oficinas),
      nom_oficinas: item.nom_oficinas,
      marca: item.marca,
      regional: item.regional,
      did: item.did !== null ? String(item.did) : '',
      cpid: item.cpid !== null ? String(item.cpid) : '',
      ind_activo: item.ind_activo,
      canales_ids: [],
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

    if (!form.nom_oficinas.trim()) {
      this.error.set('El nombre de la oficina es obligatorio');
      return;
    }
    if (!form.cpid) {
      this.error.set('La ciudad es obligatoria');
      return;
    }

    const payload: OficinaFormPayload = {
      nom_oficinas: form.nom_oficinas.trim(),
      marca: form.marca.trim(),
      regional: form.regional.trim(),
      cpid: parseInt(form.cpid, 10),
      ind_activo: form.ind_activo,
      canales_ids: form.canales_ids
        .map((strId) => parseInt(strId, 10))
        .filter((num) => Number.isFinite(num)),
    };

    try {
      const editId = this.editId();
      if (editId !== null) {
        await this.actualizarMut.mutateAsync({ codOficinas: editId, payload });
        this.success.set('Oficina actualizada correctamente');
      } else {
        await this.crearMut.mutateAsync(payload);
        this.success.set('Oficina creada correctamente');
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
