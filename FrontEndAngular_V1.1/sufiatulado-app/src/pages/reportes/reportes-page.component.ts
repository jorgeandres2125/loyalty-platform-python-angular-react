import { ChangeDetectionStrategy, Component, computed, effect, inject, signal } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../shared/api/client';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { PROGRAMA, QUERY_KEYS } from '../../shared/config/constants';
import { injectGenerarReporte, injectObtenerPreviewReporte } from '../../features/reportes/model/queries';
import { REPORTE_TIPO, type ReporteParams, type ReporteTipo } from '../../features/reportes/model/types';
import type { Subprograma } from '../../shared/api/catalogos';

interface FormState {
  tipo: ReporteTipo;
  programa: number;
  subprograma: number | '';
  fecha_inicio: string;
  fecha_fin: string;
  cedula: string;
  estado: number | '';
}

const TIPOS_REPORTE: ReadonlyArray<{ value: ReporteTipo; label: string }> = [
  { value: REPORTE_TIPO.HOJA_VIDA, label: 'Hoja de vida' },
  { value: REPORTE_TIPO.INFO_LABORAL, label: 'Información laboral' },
  { value: REPORTE_TIPO.PLANTILLA_PARTICIPANTES, label: 'Plantilla participantes' },
  { value: REPORTE_TIPO.INFO_TRIBUTARIA, label: 'Información tributaria' },
  { value: REPORTE_TIPO.USUARIOS_MIGRADOS, label: 'Usuarios migrados' },
  { value: REPORTE_TIPO.DEFAULT, label: 'Listado básico' },
  { value: REPORTE_TIPO.ESTADOS_PERFILES, label: 'Estados de perfiles' },
];

const ESTADOS_PERFIL: ReadonlyArray<{ value: number; label: string }> = [
  { value: 3, label: 'Todos' },
  { value: 0, label: 'Incompleto' },
  { value: 1, label: 'Completo' },
  { value: 2, label: 'Pendiente por documentación' },
];

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

const TIPOS_SIN_PROGRAMA: readonly ReporteTipo[] = [
  REPORTE_TIPO.INFO_LABORAL,
  REPORTE_TIPO.INFO_TRIBUTARIA,
  REPORTE_TIPO.USUARIOS_MIGRADOS,
];

function renderCell(value: string | number | boolean | null): string {
  if (value === null || value === undefined) return '';
  if (typeof value === 'boolean') return value ? 'Sí' : 'No';
  return String(value);
}

@Component({
  selector: 'app-reportes-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent],
  template: `
    <div>
      <app-page-header
        title="Reportes"
        subtitle="Genera vista previa o descarga en Excel"
        icon="bi-file-earmark-bar-graph"
      />

      <!-- Configurar reporte -->
      <div class="card shadow-sm mb-3" style="border: none">
        <div class="card-body p-4">
          <form (submit)="handleGenerarExcel($event)">
            <h6 class="fw-bold mb-3 text-sufi-navy">Configurar reporte</h6>

            @if (generar.isError()) {
              <div class="alert alert-danger py-2">
                <i class="bi bi-exclamation-circle me-2"></i>
                Error al generar el reporte. Verifica los filtros e intenta de nuevo.
              </div>
            }
            @if (generar.isSuccess()) {
              <div class="alert alert-success py-2">
                <i class="bi bi-check-circle me-2"></i>
                Reporte generado y descargado correctamente.
              </div>
            }
            @if (preview.isError()) {
              <div class="alert alert-danger py-2">
                <i class="bi bi-exclamation-circle me-2"></i>
                Error al obtener la vista previa. Verifica los filtros e intenta de nuevo.
              </div>
            }

            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label" for="rep-tipo">Tipo de reporte</label>
                <select id="rep-tipo" class="form-select" (change)="setTipo($any($event.target).value)">
                  @for (t of tiposReporte; track t.value) {
                    <option [value]="t.value" [selected]="t.value === params().tipo">{{ t.label }}</option>
                  }
                </select>
              </div>

              @if (!ocultarPrograma()) {
                <div class="col-md-6">
                  <label class="form-label" for="rep-programa">Programa</label>
                  <select id="rep-programa" class="form-select" (change)="setPrograma($any($event.target).value)">
                    <option [value]="programaMovilidad" [selected]="params().programa === programaMovilidad">
                      Movilidad (Vehículos)
                    </option>
                    <option [value]="programaConsumo" [selected]="params().programa === programaConsumo">
                      Consumo y Servicios
                    </option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label" for="rep-subprograma">Subprograma</label>
                  <select
                    id="rep-subprograma"
                    class="form-select"
                    [disabled]="subprogramaDisabled()"
                    (change)="setSubprograma($any($event.target).value)"
                  >
                    <option value="" [selected]="params().subprograma === ''">Todos</option>
                    @for (sub of subprogramasQuery.data() ?? []; track sub.cspid) {
                      <option [value]="sub.cspid" [selected]="sub.cspid === params().subprograma">
                        {{ sub.cspid_nombre }}
                      </option>
                    }
                  </select>
                </div>
              }

              <div class="col-12 col-md-6">
                <div class="row g-2">
                  <div class="col-12 col-md-6">
                    <label class="form-label" for="rep-fi">
                      Fecha inicio
                      @if (fechasObligatorias) {
                        <span class="text-danger ms-1">*</span>
                      }
                    </label>
                    <input
                      id="rep-fi"
                      type="date"
                      class="form-control"
                      [value]="params().fecha_inicio"
                      [attr.max]="params().fecha_fin || null"
                      [required]="fechasObligatorias"
                      (input)="patch({ fecha_inicio: $any($event.target).value })"
                    />
                  </div>
                  <div class="col-12 col-md-6">
                    <label class="form-label" for="rep-ff">
                      Fecha fin
                      @if (fechasObligatorias) {
                        <span class="text-danger ms-1">*</span>
                      }
                    </label>
                    <input
                      id="rep-ff"
                      type="date"
                      class="form-control"
                      [value]="params().fecha_fin"
                      [attr.min]="params().fecha_inicio || null"
                      [required]="fechasObligatorias"
                      (input)="patch({ fecha_fin: $any($event.target).value })"
                    />
                  </div>
                </div>
              </div>
              @if (errorFechas()) {
                <div class="col-12">
                  <div class="alert alert-warning py-2 mb-0">
                    <i class="bi bi-exclamation-triangle me-2"></i>{{ errorFechas() }}
                  </div>
                </div>
              }

              @if (mostrarEstadoYCedula()) {
                <div class="col-md-6">
                  <label class="form-label" for="rep-cedula">Cédula</label>
                  <input
                    id="rep-cedula"
                    type="text"
                    class="form-control"
                    placeholder="Solo dígitos"
                    [value]="params().cedula"
                    (input)="onCedula($event)"
                  />
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="rep-estado">Estado</label>
                  <select id="rep-estado" class="form-select" (change)="setEstado($any($event.target).value)">
                    <option value="" [selected]="params().estado === ''">Todos</option>
                    @for (estado of estadosFiltrables; track estado.value) {
                      <option [value]="estado.value" [selected]="estado.value === params().estado">
                        {{ estado.label }}
                      </option>
                    }
                  </select>
                </div>
              }
            </div>

            <div class="mt-4 d-flex flex-wrap gap-2">
              <button type="button" class="btn btn-primary" (click)="handleGenerarPreview()" [disabled]="preview.isPending()">
                @if (preview.isPending()) {
                  <span class="spinner-border spinner-border-sm me-2"></span>Generando…
                } @else {
                  <i class="bi bi-eye me-2"></i>Generar
                }
              </button>
              <button type="submit" class="btn btn-success" [disabled]="generar.isPending()">
                @if (generar.isPending()) {
                  <span class="spinner-border spinner-border-sm me-2"></span>Descargando…
                } @else {
                  <i class="bi bi-file-earmark-excel me-2"></i>Descargar Excel
                }
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Vista previa -->
      @if (preview.data(); as data) {
        <div class="card shadow-sm" style="border: none">
          <div class="card-body p-4">
            <div class="d-flex flex-wrap justify-content-between align-items-center mb-3 gap-2">
              <h6 class="fw-bold mb-0 text-sufi-navy">
                Vista previa
                <span class="text-muted ms-2 fw-normal">
                  ({{ data.total }} resultado{{ data.total === 1 ? '' : 's' }})
                </span>
              </h6>
              <div class="d-flex align-items-center gap-2">
                <label class="form-label mb-0 small text-muted" for="rep-pagesize">Filas por página:</label>
                <select
                  id="rep-pagesize"
                  class="form-select form-select-sm"
                  style="width: auto"
                  [disabled]="preview.isPending()"
                  (change)="cambiarPageSize(+$any($event.target).value)"
                >
                  @for (opt of pageSizeOptions; track opt) {
                    <option [value]="opt" [selected]="opt === pageSize()">{{ opt }}</option>
                  }
                </select>
              </div>
            </div>

            <div class="table-responsive" style="max-height: 60vh">
              <table class="table table-striped table-hover table-sm mb-0">
                <thead class="position-sticky top-0 bg-light" style="z-index: 1">
                  <tr>
                    @for (col of data.columns; track $index) {
                      <th class="text-nowrap">{{ col }}</th>
                    }
                  </tr>
                </thead>
                <tbody>
                  @if (data.rows.length === 0) {
                    <tr>
                      <td [attr.colspan]="data.columns.length" class="text-center text-muted py-4">
                        Sin resultados para los filtros seleccionados.
                      </td>
                    </tr>
                  } @else {
                    @for (row of data.rows; track $index) {
                      <tr>
                        @for (cell of row; track $index) {
                          <td class="text-nowrap">{{ renderCell(cell) }}</td>
                        }
                      </tr>
                    }
                  }
                </tbody>
              </table>
            </div>

            @if (data.total > 0) {
              <div class="d-flex flex-wrap justify-content-between align-items-center mt-3 gap-2">
                <span class="text-muted small">Página {{ page() }} de {{ totalPages() }}</span>
                <div class="btn-group btn-group-sm" role="group">
                  <button type="button" class="btn btn-outline-secondary" (click)="cambiarPagina(1)"
                    [disabled]="page() <= 1 || preview.isPending()">
                    <i class="bi bi-chevron-double-left"></i>
                  </button>
                  <button type="button" class="btn btn-outline-secondary" (click)="cambiarPagina(page() - 1)"
                    [disabled]="page() <= 1 || preview.isPending()">
                    <i class="bi bi-chevron-left"></i>
                  </button>
                  <button type="button" class="btn btn-outline-secondary" (click)="cambiarPagina(page() + 1)"
                    [disabled]="page() >= totalPages() || preview.isPending()">
                    <i class="bi bi-chevron-right"></i>
                  </button>
                  <button type="button" class="btn btn-outline-secondary" (click)="cambiarPagina(totalPages())"
                    [disabled]="page() >= totalPages() || preview.isPending()">
                    <i class="bi bi-chevron-double-right"></i>
                  </button>
                </div>
              </div>
            }
          </div>
        </div>
      }
    </div>
  `,
})
export class ReportesPageComponent {
  private readonly api = inject(ApiClient);

  protected readonly tiposReporte = TIPOS_REPORTE;
  protected readonly estadosFiltrables = ESTADOS_PERFIL.filter((estado) => estado.value !== 3);
  protected readonly pageSizeOptions = PAGE_SIZE_OPTIONS;
  protected readonly programaMovilidad: number = PROGRAMA.MOVILIDAD;
  protected readonly programaConsumo: number = PROGRAMA.CONSUMO;
  protected readonly fechasObligatorias: boolean = true;

  protected readonly params = signal<FormState>({
    tipo: REPORTE_TIPO.HOJA_VIDA,
    programa: PROGRAMA.MOVILIDAD,
    subprograma: '',
    fecha_inicio: '',
    fecha_fin: '',
    cedula: '',
    estado: '',
  });
  protected readonly page = signal<number>(1);
  protected readonly pageSize = signal<number>(10);
  protected readonly errorFechas = signal<string>('');

  protected readonly ocultarPrograma = computed<boolean>(() =>
    TIPOS_SIN_PROGRAMA.includes(this.params().tipo),
  );
  protected readonly mostrarEstadoYCedula = computed<boolean>(
    () => this.params().tipo === REPORTE_TIPO.ESTADOS_PERFILES,
  );

  protected readonly subprogramasQuery = injectQuery(() => {
    const programa: number = this.params().programa;
    return {
      queryKey: [QUERY_KEYS.REPORTES, 'subprogramas', programa],
      queryFn: async () => {
        const url: string = `/asesor-consumo/subprogramas/${programa}`;
        const { data } = await this.api.get<Subprograma[]>(url);
        return data;
      },
      enabled: !this.ocultarPrograma() && programa === PROGRAMA.CONSUMO,
    };
  });

  protected readonly generar = injectGenerarReporte();
  protected readonly preview = injectObtenerPreviewReporte();

  protected readonly totalPages = computed<number>(() => {
    const data = this.preview.data();
    return data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;
  });

  protected readonly subprogramaDisabled = computed<boolean>(
    () =>
      this.params().programa === PROGRAMA.MOVILIDAD ||
      this.subprogramasQuery.isLoading() ||
      (this.subprogramasQuery.data()?.length ?? 0) === 0,
  );

  constructor() {
    effect((onCleanup) => {
      if (!this.generar.isSuccess()) return;
      const timeoutId = setTimeout(() => this.generar.reset(), 10_000);
      onCleanup(() => clearTimeout(timeoutId));
    });
  }

  protected patch(cambios: Partial<FormState>): void {
    this.params.update((prev) => ({ ...prev, ...cambios }));
  }

  // Al cambiar tipo o programa se reinicia el subprograma (como el efecto del original).
  protected setTipo(valor: string): void {
    this.patch({ tipo: Number(valor) as ReporteTipo, subprograma: '' });
  }

  protected setPrograma(valor: string): void {
    this.patch({ programa: Number(valor), subprograma: '' });
  }

  protected setSubprograma(valor: string): void {
    this.patch({ subprograma: valor === '' ? '' : Number(valor) });
  }

  protected setEstado(valor: string): void {
    this.patch({ estado: valor === '' ? '' : Number(valor) });
  }

  protected onCedula(e: Event): void {
    const input = e.target as HTMLInputElement;
    const valor: string = input.value.replace(/\D/g, '');
    input.value = valor;
    this.patch({ cedula: valor });
  }

  protected renderCell(value: string | number | boolean | null): string {
    return renderCell(value);
  }

  private validarFechas(): boolean {
    this.errorFechas.set('');
    if (!this.fechasObligatorias) return true;
    const { fecha_inicio, fecha_fin } = this.params();
    if (!fecha_inicio || !fecha_fin) {
      this.errorFechas.set('Selecciona fecha inicio y fecha fin.');
      return false;
    }
    if (fecha_inicio >= fecha_fin) {
      this.errorFechas.set('La fecha inicio debe ser menor que la fecha fin.');
      return false;
    }
    return true;
  }

  private buildBaseParams(): ReporteParams {
    const params: FormState = this.params();
    const ocultar: boolean = this.ocultarPrograma();
    const mostrar: boolean = this.mostrarEstadoYCedula();
    return {
      tipo: params.tipo,
      programa: ocultar ? 1 : params.programa,
      subprograma: ocultar ? null : params.subprograma === '' ? null : Number(params.subprograma),
      fecha_inicio: params.fecha_inicio || undefined,
      fecha_fin: params.fecha_fin || undefined,
      cedula: mostrar && params.cedula ? params.cedula : undefined,
      estado: mostrar && params.estado !== '' ? Number(params.estado) : undefined,
    };
  }

  protected handleGenerarExcel(e: Event): void {
    e.preventDefault();
    if (!this.validarFechas()) return;
    this.generar.mutate(this.buildBaseParams());
  }

  protected handleGenerarPreview(): void {
    if (!this.validarFechas()) return;
    this.page.set(1);
    this.preview.mutate({ ...this.buildBaseParams(), page: 1, page_size: this.pageSize() });
  }

  protected cambiarPagina(nuevaPagina: number): void {
    if (nuevaPagina < 1 || nuevaPagina > this.totalPages()) return;
    this.page.set(nuevaPagina);
    this.preview.mutate({ ...this.buildBaseParams(), page: nuevaPagina, page_size: this.pageSize() });
  }

  protected cambiarPageSize(nuevoSize: number): void {
    this.pageSize.set(nuevoSize);
    this.page.set(1);
    this.preview.mutate({ ...this.buildBaseParams(), page: 1, page_size: nuevoSize });
  }
}
