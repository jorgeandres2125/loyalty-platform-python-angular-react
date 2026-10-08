import { ChangeDetectionStrategy, Component, computed, effect, signal, untracked } from '@angular/core';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { TomSelectMultiFieldComponent } from '../../shared/ui/components/tom-select-multi-field.component';
import type { TomSelectOption } from '../../shared/ui/components/tom-select-field.component';
import { EstadoSwitchComponent } from '../../shared/ui/components/estado-switch.component';
import { leerInput } from '../../shared/lib/inputs';
import {
  injectActualizarCanal,
  injectCanal,
  injectCanales,
  injectCrearCanal,
} from '../../features/canales/model/queries';
import type { CanalFormPayload, CanalListItem } from '../../features/canales/model/types';
import { injectOficinasActivas } from '../../features/oficinas/model/queries';
import { injectProgramas, injectSubprogramas } from '../../features/programas/model/queries';
import type { SubprogramaItem } from '../../features/programas/model/types';

type Tab = 'lista' | 'registro';

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

const ESTADO_OPTIONS: ReadonlyArray<{ value: string; label: string }> = [
  { value: '', label: 'Todos' },
  { value: 'true', label: 'Activos' },
  { value: 'false', label: 'Inactivos' },
];

const PROGRAMA_BADGE_BG: Record<number, string> = {
  1: 'primary',
  2: 'success',
};

const CPID_MOVILIDAD: number = 1;

interface FormState {
  nom_canales: string;
  cpid: string;
  cspid: string;
  ind_activo: boolean;
  id_canales: string;
  oficinas_ids: string[];
}

const initForm: FormState = {
  nom_canales: '',
  cpid: '',
  cspid: '',
  ind_activo: true,
  id_canales: '0',
  oficinas_ids: [],
};

@Component({
  selector: 'app-canales-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, TomSelectMultiFieldComponent, EstadoSwitchComponent],
  template: `
    <div>
      <app-page-header title="Canales" [subtitle]="subtitulo()" icon="bi-diagram-3" />

      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white border-bottom-0 pb-0">
          <ul class="nav nav-tabs">
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'lista'" (click)="tab.set('lista')">
                <i class="bi bi-list-ul me-2"></i>Lista de Canales
              </button>
            </li>
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'registro'" (click)="tab.set('registro')">
                <i class="bi me-2" [class]="isEditing() ? 'bi-pencil-square' : 'bi-plus-circle'"></i>
                {{ isEditing() ? 'Editar Canal' : 'Nuevo Canal' }}
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
              <div class="d-flex align-items-end gap-2 flex-wrap">
                <div style="min-width: 220px">
                  <label class="form-label small mb-1">Nombre</label>
                  <input class="form-control form-control-sm" type="text" placeholder="Filtrar por nombre..."
                    [value]="searchNombre()" (input)="searchNombre.set(leer($event))"
                    (keydown.enter)="handleBuscar()" maxlength="120" />
                </div>
                <div style="min-width: 140px">
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
                  <i class="bi bi-plus-lg me-1"></i>Nuevo Canal
                </button>
              </div>
            </div>

            @if (lista.isLoading()) {
              <div class="text-center py-5"><div class="spinner-border" role="status"></div></div>
            } @else if (lista.isError()) {
              <div class="alert alert-danger m-3">Error al cargar canales</div>
            } @else if (!lista.data() || lista.data()!.items.length === 0) {
              <div class="text-center py-5 text-muted">
                <i class="bi bi-inbox display-4 d-block mb-2"></i>
                No se encontraron canales
              </div>
            } @else {
              <div class="table-responsive">
                <table class="table table-hover mb-0 align-middle">
                  <thead class="table-light">
                    <tr>
                      <th>Código</th>
                      <th>Nombre</th>
                      <th>Programa</th>
                      <th>Subprograma</th>
                      <th>Estado</th>
                      <th class="text-end">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (canal of lista.data()!.items; track canal.cod_canales) {
                      @let nombrePrograma = canal.cpid !== null ? programaPorCpid().get(canal.cpid) : undefined;
                      @let nombreSubprograma = canal.cspid !== null && canal.cspid > 0 ? subprogramaPorCspid().get(canal.cspid) : undefined;
                      <tr>
                        <td><code>{{ canal.cod_canales }}</code></td>
                        <td class="fw-semibold">{{ canal.nom_canales }}</td>
                        <td>
                          @if (canal.cpid !== null && nombrePrograma) {
                            <span class="badge" [class]="'bg-' + programaBadge(canal.cpid)">{{ nombrePrograma }}</span>
                          } @else {
                            <span class="text-muted">—</span>
                          }
                        </td>
                        <td>
                          @if (canal.cpid === cpidMovilidad) {
                            <span class="text-muted fst-italic">Sin subprograma</span>
                          } @else if (nombreSubprograma) {
                            <span>{{ nombreSubprograma }}</span>
                          } @else {
                            <span class="text-muted">—</span>
                          }
                        </td>
                        <td>
                          <span class="badge" [class]="canal.ind_activo ? 'bg-success' : 'bg-secondary'">
                            {{ canal.ind_activo ? 'Activo' : 'Inactivo' }}
                          </span>
                        </td>
                        <td class="text-end">
                          <button type="button" class="btn btn-sm btn-outline-primary" (click)="handleEditar(canal)">
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
                <div class="col-12">
                  <label class="form-label" for="canal-nombre">Nombre del canal <span class="text-danger">*</span></label>
                  <input id="canal-nombre" class="form-control" type="text" [value]="f.nom_canales"
                    (input)="patch({ nom_canales: leer($event) })" placeholder="Ej. AUTOMONTANA" maxlength="120" required />
                </div>

                <div class="col-md-4">
                  <label class="form-label" for="canal-programa">Programa</label>
                  <select id="canal-programa" class="form-select" (change)="handleProgramaChange($any($event.target).value)">
                    <option value="" [selected]="f.cpid === ''">— Sin programa —</option>
                    @for (p of programas(); track p.cpid) {
                      <option [value]="p.cpid" [selected]="'' + p.cpid === f.cpid">{{ p.cp_nombre }}</option>
                    }
                  </select>
                </div>

                <div class="col-md-4">
                  <label class="form-label" for="canal-subprograma">Subprograma</label>
                  <select id="canal-subprograma" class="form-select" [disabled]="subprogramaDisabled()"
                    (change)="patch({ cspid: $any($event.target).value })">
                    @if (cpidNum() === cpidMovilidad) {
                      <option value="0" selected>Sin subprograma</option>
                    } @else {
                      <option value="" [selected]="f.cspid === ''">— Seleccionar —</option>
                      @for (sp of subprogramasFiltrados(); track sp.cspid) {
                        <option [value]="sp.cspid" [selected]="'' + sp.cspid === f.cspid">{{ sp.cspid_nombre }}</option>
                      }
                    }
                  </select>
                  <div class="form-text text-muted">{{ ayudaSubprograma() }}</div>
                </div>

                <div class="col-md-4 d-flex align-items-end">
                  <app-estado-switch id="canal-estado" [checked]="f.ind_activo" (checkedChange)="patch({ ind_activo: $event })" />
                </div>

                <div class="col-12">
                  <label class="form-label" for="canal-oficinas">
                    Oficinas asociadas
                    @if (oficinasActivasQ.isLoading()) {
                      <span class="spinner-border spinner-border-sm ms-2"></span>
                    }
                  </label>
                  <app-tom-select-multi-field
                    id="canal-oficinas"
                    [options]="oficinaOpts()"
                    [value]="f.oficinas_ids"
                    (valueChange)="patch({ oficinas_ids: $event })"
                    placeholder="— Seleccionar una o varias oficinas —"
                    [disabled]="oficinasActivasQ.isLoading()"
                  />
                  <div class="form-text text-muted">{{ ayudaOficinas() }}</div>
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
export class CanalesPageComponent {
  protected readonly pageSizeOptions = PAGE_SIZE_OPTIONS;
  protected readonly estadoOptions = ESTADO_OPTIONS;
  protected readonly cpidMovilidad = CPID_MOVILIDAD;
  protected readonly leer = leerInput;

  protected readonly tab = signal<Tab>('lista');
  protected readonly page = signal<number>(1);
  protected readonly pageSize = signal<number>(10);
  protected readonly searchNombre = signal<string>('');
  protected readonly searchEstado = signal<string>('');
  private readonly filtroNombre = signal<string>('');
  private readonly filtroEstado = signal<string>('');

  protected readonly editId = signal<number | null>(null);
  protected readonly form = signal<FormState>(initForm);
  protected readonly error = signal<string>('');
  protected readonly success = signal<string>('');

  protected readonly lista = injectCanales(() => {
    const estado: string = this.filtroEstado();
    return {
      page: this.page(),
      page_size: this.pageSize(),
      nombre: this.filtroNombre() || undefined,
      ind_activo: estado === '' ? undefined : estado === 'true',
    };
  });
  private readonly programasQ = injectProgramas();
  private readonly subprogramasQ = injectSubprogramas();
  protected readonly oficinasActivasQ = injectOficinasActivas();
  private readonly canalEditQ = injectCanal(() => this.editId());
  private readonly crearMut = injectCrearCanal();
  private readonly actualizarMut = injectActualizarCanal();

  protected readonly programas = computed(() => this.programasQ.data() ?? []);
  private readonly subprogramas = computed<SubprogramaItem[]>(() => this.subprogramasQ.data() ?? []);
  protected readonly programaPorCpid = computed<Map<number, string>>(
    () => new Map(this.programas().map((p) => [p.cpid, p.cp_nombre])),
  );
  protected readonly subprogramaPorCspid = computed<Map<number, string>>(
    () => new Map(this.subprogramas().map((sp) => [sp.cspid, sp.cspid_nombre])),
  );

  protected readonly filtrosActivos = computed<boolean>(() => !!this.filtroNombre() || this.filtroEstado() !== '');
  protected readonly totalPages = computed<number>(() => {
    const data = this.lista.data();
    return data ? Math.max(1, Math.ceil(data.total / this.pageSize())) : 1;
  });
  protected readonly isEditing = computed<boolean>(() => this.editId() !== null);
  protected readonly isSaving = computed<boolean>(() => this.crearMut.isPending() || this.actualizarMut.isPending());
  protected readonly subtitulo = computed<string | undefined>(() => {
    const data = this.lista.data();
    return data ? `${data.total} canales${this.filtrosActivos() ? ' encontrados' : ''}` : undefined;
  });

  // ── Formulario ──
  protected readonly cpidNum = computed<number | null>(() => {
    const cpid: string = this.form().cpid;
    return cpid === '' ? null : parseInt(cpid, 10);
  });
  protected readonly subprogramasFiltrados = computed<SubprogramaItem[]>(() => {
    const cpid = this.cpidNum();
    return cpid === null ? [] : this.subprogramas().filter((sp) => sp.cpid === cpid);
  });
  protected readonly subprogramaDisabled = computed<boolean>(() => {
    const cpid = this.cpidNum();
    return cpid === null || cpid === CPID_MOVILIDAD;
  });
  protected readonly ayudaSubprograma = computed<string>(() => {
    const cpid = this.cpidNum();
    if (cpid === CPID_MOVILIDAD) return 'Movilidad no usa subprograma.';
    if (cpid === null) return 'Selecciona un programa primero.';
    return `${this.subprogramasFiltrados().length} subprogramas disponibles.`;
  });
  protected readonly oficinaOpts = computed<TomSelectOption[]>(() =>
    (this.oficinasActivasQ.data() ?? []).map((o) => ({ value: String(o.cod_oficinas), label: o.nom_oficinas })),
  );
  protected readonly ayudaOficinas = computed<string>(() => {
    const n: number = this.form().oficinas_ids.length;
    if (n === 0) return 'Un canal puede asociarse a varias oficinas.';
    return `${n} oficina${n === 1 ? '' : 's'} seleccionada${n === 1 ? '' : 's'}.`;
  });

  constructor() {
    // Cuando se está editando y llega el detalle del canal, sincroniza oficinas_ids.
    effect(() => {
      const editId = this.editId();
      const data = this.canalEditQ.data();
      if (!editId || !data || data.cod_canales !== editId) return;
      untracked(() => this.patch({ oficinas_ids: data.oficinas_ids.map((id) => String(id)) }));
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

  protected programaBadge(cpid: number): string {
    return PROGRAMA_BADGE_BG[cpid] ?? 'secondary';
  }

  protected patch(cambios: Partial<FormState>): void {
    this.form.update((prev) => ({ ...prev, ...cambios }));
  }

  protected setPageSize(n: number): void {
    this.pageSize.set(n);
    this.page.set(1);
  }

  protected handleProgramaChange(value: string): void {
    if (value === '') {
      this.patch({ cpid: '', cspid: '' });
      return;
    }
    const cpidNum: number = parseInt(value, 10);
    if (cpidNum === CPID_MOVILIDAD) {
      // Movilidad (Vehículos) no tiene subprograma → cspid = 0
      this.patch({ cpid: value, cspid: '0' });
    } else {
      this.patch({ cpid: value, cspid: '' });
    }
  }

  protected handleBuscar(): void {
    this.filtroNombre.set(this.searchNombre().trim());
    this.filtroEstado.set(this.searchEstado());
    this.page.set(1);
  }

  protected handleLimpiar(): void {
    this.searchNombre.set('');
    this.searchEstado.set('');
    this.filtroNombre.set('');
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

  protected handleEditar(item: CanalListItem): void {
    this.editId.set(item.cod_canales);
    this.form.set({
      nom_canales: item.nom_canales,
      cpid: item.cpid === null ? '' : String(item.cpid),
      cspid: item.cspid === null ? '' : String(item.cspid),
      ind_activo: item.ind_activo,
      id_canales: String(item.id_canales ?? 0),
      oficinas_ids: [],
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

    if (!form.nom_canales.trim()) {
      this.error.set('El nombre del canal es obligatorio');
      return;
    }

    const payload: CanalFormPayload = {
      nom_canales: form.nom_canales.trim(),
      cpid: form.cpid.trim() === '' ? null : parseInt(form.cpid, 10),
      cspid: form.cspid.trim() === '' ? null : parseInt(form.cspid, 10),
      ind_activo: form.ind_activo,
      oficinas_ids: form.oficinas_ids
        .map((strId) => parseInt(strId, 10))
        .filter((num) => Number.isFinite(num)),
    };

    try {
      const editId = this.editId();
      if (editId !== null) {
        await this.actualizarMut.mutateAsync({ codCanales: editId, payload });
        this.success.set('Canal actualizado correctamente');
      } else {
        await this.crearMut.mutateAsync(payload);
        this.success.set('Canal creado correctamente');
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
