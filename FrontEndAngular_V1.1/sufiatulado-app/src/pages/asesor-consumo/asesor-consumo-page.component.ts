import { ChangeDetectionStrategy, Component, computed, effect, inject, signal, untracked } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../shared/api/client';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { ConfirmModalComponent } from '../../shared/ui/components/confirm-modal.component';
import { EstadoSwitchComponent } from '../../shared/ui/components/estado-switch.component';
import {
  TomSelectBuscadorComponent,
  type OpcionBuscador,
} from '../../shared/ui/components/tom-select-buscador.component';
import { WizardStepperComponent, type PasoWizard } from '../../widgets/wizard-stepper/wizard-stepper.component';
import { PerfilEmocionalCamposComponent } from '../../widgets/perfil-emocional/perfil-emocional-campos.component';
import {
  INIT_EMOCIONAL,
  mapearEmocional,
  payloadEmocional,
  type FormEmocional,
} from '../../widgets/perfil-emocional/perfil-emocional';
import {
  injectAsesorConsumoList,
  injectDetalleAsesorConsumo,
  injectFinalizarConsumo,
  injectSubprogramasConsumo,
  injectWizardPaso1Consumo,
  injectWizardPaso3Consumo,
} from '../../features/asesor-consumo/model/queries';
import { AsesorConsumoApi } from '../../features/asesor-consumo/model/apiAsesorConsumo';
import type { AsesorConsumoFiltros } from '../../features/asesor-consumo/model/types';
import { injectCambiarEstadoComisionista } from '../../features/admin-usuarios/model/queries';
import { parseGenero, parseTipoDoc, refObj, strDe } from '../../shared/lib/parseContacto';
import { leerInput, soloDigitos } from '../../shared/lib/inputs';

const PROGRAMA_CONSUMO_ID = 2 as const;

type Tab = 'lista' | 'registro';
type WizardStep = 1 | 2 | 3;

const PASOS: readonly PasoWizard[] = [
  { label: 'Contacto', icon: 'bi-person' },
  { label: 'Perfil Emocional', icon: 'bi-heart' },
  { label: 'Confirmación', icon: 'bi-check-circle' },
];

const TIPOS_DOC: ReadonlyArray<{ value: string; label: string }> = [
  { value: 'CC', label: 'C.C.' },
  { value: 'CE', label: 'C.E.' },
  { value: 'F&I', label: 'F&I' },
  { value: 'GC', label: 'GC' },
  { value: 'PEP', label: 'PEP' },
  { value: 'PPT', label: 'PPT' },
  { value: 'VDA', label: 'VDA' },
];

const GENEROS: readonly string[] = ['Masculino', 'Femenino', 'Otro'];

interface FormContacto {
  numero_documento: string;
  tipo_documento: string;
  nombre_completo: string;
  genero: string;
  fecha_nacimiento: string;
  celular: string;
  telefono: string;
  email: string;
  direccion: string;
  departamento: string;
  ciudad: string;
  comisionista_subprograma_id: number | '';
  cod_canales: number | '';
  cod_oficinas: number | '';
  acepto_habeas_data: boolean;
  incentivos: boolean;
  estado: 0 | 1 | null;
  firma_contrato: boolean | null;
}

const initContacto: FormContacto = {
  numero_documento: '',
  tipo_documento: 'CC',
  nombre_completo: '',
  genero: '',
  fecha_nacimiento: '',
  celular: '',
  telefono: '',
  email: '',
  direccion: '',
  departamento: '',
  ciudad: '',
  comisionista_subprograma_id: 2,
  cod_canales: '',
  cod_oficinas: '',
  acepto_habeas_data: false,
  incentivos: false,
  estado: 1,
  firma_contrato: null,
};

const GENERO_CONSUMO: Record<string, string> = {
  '0': 'Femenino',
  '1': 'Masculino',
  F: 'Femenino',
  M: 'Masculino',
  Femenino: 'Femenino',
  Masculino: 'Masculino',
  Otro: 'Otro',
  O: 'Otro',
};

function estadoConsumo(v: unknown): 0 | 1 | null {
  if (v === undefined || v === null) return null;
  return Number(v) === 1 ? 1 : 0;
}

function mapearContactoConsumoReg(
  c: Record<string, unknown>,
  documentoEditar: string | null,
): { form: FormContacto; selectedDid: number | null } {
  const depObj = refObj(c['departamento']);
  const ciuObj = refObj(c['ciudad']);
  const form: FormContacto = {
    numero_documento: String(c['numero_documento'] ?? documentoEditar),
    tipo_documento: parseTipoDoc(c['tipo_documento']),
    nombre_completo: strDe(c['nombre_completo']),
    genero: parseGenero(c['genero'], GENERO_CONSUMO),
    fecha_nacimiento: c['fecha_nacimiento'] ? String(c['fecha_nacimiento']) : '',
    celular: strDe(c['celular']),
    telefono: strDe(c['telefono']),
    email: c['email'] ? String(c['email']) : '',
    direccion: strDe(c['direccion']),
    departamento: depObj ? strDe(depObj['did']) : strDe(c['departamento']),
    ciudad: ciuObj ? strDe(ciuObj['cid']) : strDe(c['ciudad']),
    comisionista_subprograma_id: c['comisionista_subprograma_id'] ? Number(c['comisionista_subprograma_id']) : 2,
    cod_canales: (c['cod_canales'] as number) ?? '',
    cod_oficinas: (c['cod_oficinas'] as number) ?? '',
    acepto_habeas_data: Boolean(c['acepto_habeas_data']),
    incentivos: Boolean(c['incentivos']),
    estado: estadoConsumo(c['estado']),
    firma_contrato:
      c['firma_contrato'] !== undefined && c['firma_contrato'] !== null ? Boolean(c['firma_contrato']) : null,
  };
  const did = depObj?.['did'];
  return { form, selectedDid: typeof did === 'number' ? did : null };
}

function detalleError(err: unknown, fallback: string): string {
  const msg = (err as { response?: { data?: { detail?: string | string[] } } })?.response?.data?.detail;
  return Array.isArray(msg) ? msg.join(' | ') : (msg ?? fallback);
}

function dash(v: string): string {
  return v || '—';
}

function nombreEn<T>(items: T[] | undefined, match: (x: T) => boolean, get: (x: T) => string | null): string {
  const found = items?.find(match);
  return (found ? get(found) : null) ?? '—';
}

function etiquetaTipoDoc(t: string): string {
  if (t === 'CC') return 'C.C.';
  if (t === 'CE') return 'C.E.';
  if (t === 'NIT') return 'NIT';
  return t || '—';
}

function etiquetaEstado(e: 0 | 1 | null): string {
  if (e === 1) return 'Activo';
  if (e === 0) return 'Inactivo';
  return '—';
}

function etiquetaFirma(f: boolean | null): string {
  if (f === true) return 'Sí';
  if (f === false) return 'No';
  return '—';
}

interface Departamento {
  did: number;
  departamento: string;
}
interface Ciudad {
  cid: number;
  ciudad: string;
}
interface Canal {
  cod_canales: number;
  nom_canales: string;
  cpid: number;
  cspid: number;
}
interface Oficina {
  cod_oficinas: number;
  nom_oficinas: string | null;
}

@Component({
  selector: 'app-asesor-consumo-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    PageHeaderComponent,
    ConfirmModalComponent,
    EstadoSwitchComponent,
    TomSelectBuscadorComponent,
    WizardStepperComponent,
    PerfilEmocionalCamposComponent,
  ],
  template: `
    <div>
      <app-page-header
        title="Asesor Consumo"
        subtitle="Gestión de asesores del programa Consumo y Servicios"
        icon="bi-person-plus-fill"
      >
        @if (tab() === 'lista') {
          <button actions type="button" class="btn btn-danger btn-sm" (click)="nuevoRegistro()">
            <i class="bi bi-plus-circle me-1"></i>Nuevo Asesor
          </button>
        }
      </app-page-header>

      @if (cuentaMsg()) {
        <div class="alert alert-success alert-dismissible">
          <i class="bi bi-check-circle me-2"></i>
          {{ cuentaMsg() }}
          <button type="button" class="btn-close" aria-label="Close" (click)="cuentaMsg.set('')"></button>
        </div>
      }

      <div class="card shadow-sm" style="border: none">
        <div class="card-header bg-white border-0 pt-3">
          <ul class="nav nav-tabs">
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'lista'" (click)="tab.set('lista')">
                <i class="bi bi-people me-2"></i>Lista de Asesores
              </button>
            </li>
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'registro'" (click)="tab.set('registro')">
                <i class="bi bi-person-plus me-2"></i>
                {{ documentoEditar() ? 'Editar Asesor' : 'Registro' }}
              </button>
            </li>
          </ul>
        </div>

        <div class="card-body" [class]="tab() === 'lista' ? 'p-0' : 'p-4'">
          <!-- ── TAB LISTA ── -->
          @if (tab() === 'lista') {
            <div class="d-flex align-items-center justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
              <small class="text-muted">
                @if (lista.data(); as data) {
                  {{ data.total }} {{ filtrosActivos() ? 'asesores encontrados' : 'asesores registrados' }}
                }
              </small>
              <select class="form-select form-select-sm" style="width: auto" (change)="setSize(+$any($event.target).value)">
                @for (n of [10, 20, 30]; track n) {
                  <option [value]="n" [selected]="n === size()">Ver {{ n }} por página</option>
                }
              </select>
            </div>

            <!-- ── Panel de búsqueda ── -->
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
            } @else if (lista.data()?.items?.length === 0) {
              <div class="text-center py-5 text-muted">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                Sin asesores de Consumo registrados
              </div>
            } @else {
              <div class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Documento</th>
                      <th>Tipo Doc.</th>
                      <th>Género</th>
                      <th>Nombre</th>
                      <th>Celular</th>
                      <th>Subprograma</th>
                      <th>Departamento</th>
                      <th>Ciudad</th>
                      <th>Estado</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (a of lista.data()?.items ?? []; track a.numero_documento) {
                      <tr style="cursor: pointer" (click)="abrirEdicion(a.numero_documento)">
                        <td class="font-monospace">{{ a.numero_documento }}</td>
                        <td>{{ a.tipo_documento?.nombre ?? '—' }}</td>
                        <td>{{ a.genero?.nombre ?? '—' }}</td>
                        <td>{{ a.nombre_completo ?? '—' }}</td>
                        <td>{{ a.celular ?? '—' }}</td>
                        <td>{{ a.subprograma?.cspid_nombre ?? '—' }}</td>
                        <td>{{ a.departamento?.departamento ?? '—' }}</td>
                        <td>{{ a.ciudad?.ciudad ?? '—' }}</td>
                        <td>
                          <span class="badge" [class]="a.estado === 1 ? 'bg-success' : 'bg-secondary'">
                            {{ a.estado === 1 ? 'Activo' : 'Inactivo' }}
                          </span>
                        </td>
                        <td (click)="$event.stopPropagation()">
                          <button type="button" class="btn btn-outline-secondary btn-sm me-1" title="Editar"
                            (click)="abrirEdicion(a.numero_documento)">
                            <i class="bi bi-pencil"></i>
                          </button>
                          <button type="button" class="btn btn-outline-danger btn-sm" title="Deshabilitar cuenta de acceso"
                            (click)="cuentaObjetivo.set({ doc: a.numero_documento, nombre: a.nombre_completo ?? a.numero_documento })">
                            <i class="bi bi-person-fill-slash"></i>
                          </button>
                        </td>
                      </tr>
                    }
                  </tbody>
                </table>
              </div>
            }

            @if (lista.data(); as data) {
              @if (data.pages > 1) {
                <div class="d-flex justify-content-center align-items-center gap-2 py-3">
                  <button type="button" class="btn btn-outline-secondary btn-sm" [disabled]="page() === 1" (click)="page.set(1)"
                    title="Primera página">
                    <i class="bi bi-chevron-double-left"></i>
                  </button>
                  <button type="button" class="btn btn-outline-secondary btn-sm" [disabled]="page() === 1"
                    (click)="page.set(page() - 1)" title="Página anterior">
                    <i class="bi bi-chevron-left"></i>
                  </button>
                  <span class="small">Página {{ page() }} de {{ data.pages }}</span>
                  <button type="button" class="btn btn-outline-secondary btn-sm" [disabled]="page() === data.pages"
                    (click)="page.set(page() + 1)" title="Página siguiente">
                    <i class="bi bi-chevron-right"></i>
                  </button>
                  <button type="button" class="btn btn-outline-secondary btn-sm" [disabled]="page() === data.pages"
                    (click)="page.set(data.pages)" title="Última página">
                    <i class="bi bi-chevron-double-right"></i>
                  </button>
                </div>
              }
            }
          }

          <!-- ── TAB REGISTRO / EDICIÓN ── -->
          @if (tab() === 'registro') {
            @if (documentoEditar() && (!formReady() || detalle.isLoading())) {
              <div class="text-center py-4"><div class="spinner-border text-danger" role="status"></div></div>
            }

            @if ((!documentoEditar() || formReady()) && !detalle.isLoading()) {
              <app-wizard-stepper [steps]="pasos" [step]="step()" />
              @if (error()) {
                <div class="alert alert-danger alert-dismissible">
                  {{ error() }}
                  <button type="button" class="btn-close" aria-label="Close" (click)="error.set('')"></button>
                </div>
              }

              @switch (step()) {
                <!-- ── Paso 1: Contacto ── -->
                @case (1) {
                  @let c = contacto();
                  <form (submit)="handlePaso1($event)">
                    <h6 class="mb-3 fw-semibold text-danger">
                      <i class="bi bi-person-lines-fill me-2"></i>Información de Contacto
                    </h6>
                    <div class="row g-3">
                      <div class="col-md-4">
                        <label class="form-label"><i class="bi bi-person-badge me-1 text-danger"></i>Tipo Documento</label>
                        <select class="form-select" (change)="patchC({ tipo_documento: $any($event.target).value })">
                          @for (t of tiposDoc; track t.value) {
                            <option [value]="t.value" [selected]="t.value === c.tipo_documento">{{ t.label }}</option>
                          }
                        </select>
                      </div>
                      <div class="col-md-4">
                        <label class="form-label"><i class="bi bi-hash me-1 text-danger"></i>Número Documento *</label>
                        <input class="form-control" required [value]="c.numero_documento"
                          (input)="patchC({ numero_documento: leer($event) })" placeholder="Solo dígitos"
                          [disabled]="!!documentoEditar()" />
                      </div>
                      <div class="col-md-4">
                        <label class="form-label"><i class="bi bi-person me-1 text-danger"></i>Nombre Completo *</label>
                        <input class="form-control" required [value]="c.nombre_completo"
                          (input)="patchC({ nombre_completo: leer($event) })" />
                      </div>
                      <div class="col-md-3">
                        <label class="form-label"><i class="bi bi-gender-ambiguous me-1 text-danger"></i>Género *</label>
                        <select class="form-select" required (change)="patchC({ genero: $any($event.target).value })">
                          <option value="" [selected]="c.genero === ''">Seleccione...</option>
                          @for (g of generos; track g) {
                            <option [value]="g" [selected]="g === c.genero">{{ g }}</option>
                          }
                        </select>
                      </div>
                      <div class="col-md-3">
                        <label class="form-label"><i class="bi bi-calendar-date me-1 text-danger"></i>Fecha Nacimiento *</label>
                        <input class="form-control" required type="date" [value]="c.fecha_nacimiento"
                          (input)="patchC({ fecha_nacimiento: leer($event) })" />
                      </div>
                      <div class="col-md-3">
                        <label class="form-label"><i class="bi bi-phone me-1 text-danger"></i>Celular * (10 dígitos)</label>
                        <input class="form-control" required inputmode="numeric" [value]="c.celular"
                          (input)="patchC({ celular: leer($event, soloDigitos) })" maxlength="10" />
                      </div>
                      <div class="col-md-3">
                        <label class="form-label"><i class="bi bi-telephone me-1 text-danger"></i>Teléfono</label>
                        <input class="form-control" inputmode="numeric" [value]="c.telefono"
                          (input)="patchC({ telefono: leer($event, soloDigitos) })" />
                      </div>
                      <div class="col-md-6">
                        <label class="form-label"><i class="bi bi-envelope me-1 text-danger"></i>Correo electrónico</label>
                        <input class="form-control" type="email" [value]="c.email" (input)="patchC({ email: leer($event) })"
                          placeholder="ejemplo@correo.com" maxlength="254" />
                      </div>
                      <div class="col-md-6">
                        <label class="form-label"><i class="bi bi-geo-alt me-1 text-danger"></i>Dirección *</label>
                        <input class="form-control" required [value]="c.direccion" (input)="patchC({ direccion: leer($event) })" />
                      </div>
                      <div class="col-md-4">
                        <label class="form-label"><i class="bi bi-map me-1 text-danger"></i>Departamento *</label>
                        <app-tom-select-buscador
                          [options]="depOpts()"
                          [value]="c.departamento"
                          (valueChange)="onDepartamento($event)"
                          placeholder="Seleccione departamento..."
                        />
                      </div>
                      <div class="col-md-4">
                        <label class="form-label"><i class="bi bi-pin-map me-1 text-danger"></i>Ciudad *</label>
                        <app-tom-select-buscador
                          [options]="ciudadOpts()"
                          [value]="c.ciudad"
                          (valueChange)="patchC({ ciudad: $event })"
                          [placeholder]="c.departamento ? 'Seleccione ciudad...' : 'Seleccione un departamento primero'"
                          [locked]="!c.departamento"
                        />
                      </div>
                      <div class="col-md-4">
                        <label class="form-label"><i class="bi bi-diagram-2 me-1 text-danger"></i>Subprograma</label>
                        <select class="form-select" (change)="onSubprograma($any($event.target).value)">
                          <option value="" [selected]="c.comisionista_subprograma_id === ''">Seleccione...</option>
                          @for (sp of subprogramas.data() ?? []; track sp.cspid) {
                            <option [value]="sp.cspid" [selected]="sp.cspid === c.comisionista_subprograma_id">
                              {{ sp.cspid_nombre }}
                            </option>
                          }
                        </select>
                      </div>
                      <div class="col-md-6">
                        <label class="form-label"><i class="bi bi-broadcast me-1 text-danger"></i>Canal</label>
                        <app-tom-select-buscador
                          [options]="canalOpts()"
                          [value]="c.cod_canales === '' ? '' : '' + c.cod_canales"
                          (valueChange)="onCanal($event)"
                          [placeholder]="canalOpts().length === 0 ? 'Sin canales disponibles' : 'Seleccione canal...'"
                          [locked]="canalOpts().length === 0"
                        />
                      </div>
                      <div class="col-md-6">
                        <label class="form-label"><i class="bi bi-building me-1 text-danger"></i>Oficina</label>
                        <app-tom-select-buscador
                          [options]="oficinaOpts()"
                          [value]="c.cod_oficinas === '' ? '' : '' + c.cod_oficinas"
                          (valueChange)="patchC({ cod_oficinas: $event !== '' ? +$event : '' })"
                          [placeholder]="placeholderOficina()"
                          [disabled]="!(c.cod_canales !== '' && oficinaOpts().length > 0)"
                        />
                      </div>
                      <div class="col-12 col-md-6">
                        <div>
                          <app-estado-switch
                            id="asesor-consumo-estado"
                            [checked]="c.estado === 1"
                            (checkedChange)="patchC({ estado: $event ? 1 : 0 })"
                          />
                        </div>
                      </div>
                      <div class="col-12">
                        <label class="form-label"><i class="bi bi-file-earmark-check me-1 text-danger"></i>Firma de Contrato</label>
                        <div class="d-flex gap-4 flex-wrap">
                          <div class="form-check">
                            <input class="form-check-input" type="radio" id="firma-contrato-si" name="firma_contrato"
                              [checked]="c.firma_contrato === true" (change)="patchC({ firma_contrato: true })" />
                            <label class="form-check-label" for="firma-contrato-si">El contrato fue firmado</label>
                          </div>
                          <div class="form-check">
                            <input class="form-check-input" type="radio" id="firma-contrato-no" name="firma_contrato"
                              [checked]="c.firma_contrato === false" (change)="patchC({ firma_contrato: false })" />
                            <label class="form-check-label" for="firma-contrato-no">No requiere firma de Contrato</label>
                          </div>
                        </div>
                      </div>
                      <div class="col-12">
                        <div class="form-check">
                          <input class="form-check-input" type="checkbox" id="habeas-data-consumo" [checked]="c.acepto_habeas_data"
                            (change)="patchC({ acepto_habeas_data: $any($event.target).checked })" />
                          <label class="form-check-label" for="habeas-data-consumo">
                            Acepto el tratamiento de datos personales (Habeas Data) *
                          </label>
                        </div>
                      </div>
                      <div class="col-12">
                        <div class="form-check">
                          <input class="form-check-input" type="checkbox" id="incentivos-consumo" [checked]="c.incentivos"
                            (change)="patchC({ incentivos: $any($event.target).checked })" />
                          <label class="form-check-label" for="incentivos-consumo">Tiene Incentivos</label>
                        </div>
                      </div>
                    </div>
                    <div class="wizard-nav mt-4">
                      <button type="button" class="btn btn-outline-secondary" (click)="tab.set('lista')">
                        <i class="bi bi-arrow-left me-1"></i>Cancelar
                      </button>
                      <button type="submit" class="btn btn-danger" [disabled]="isBusy()">
                        @if (paso1Mut.isPending()) {
                          <span class="spinner-border spinner-border-sm me-1"></span>
                        } @else {
                          <i class="bi bi-arrow-right me-1"></i>
                        }
                        Siguiente
                      </button>
                    </div>
                  </form>
                }

                <!-- ── Paso 2: Perfil Emocional ── -->
                @case (2) {
                  <form (submit)="handlePaso3($event)">
                    <app-perfil-emocional-campos
                      [(emocional)]="emocional"
                      [profesiones]="profesionOpts()"
                      persona="tercera"
                      terminosId="terminos-consumo"
                    />
                    <div class="wizard-nav mt-4">
                      <button type="button" class="btn btn-outline-secondary" (click)="step.set(1)">
                        <i class="bi bi-arrow-left me-1"></i>Anterior
                      </button>
                      <button type="submit" class="btn btn-danger" [disabled]="isBusy()">
                        @if (paso3Mut.isPending()) {
                          <span class="spinner-border spinner-border-sm me-1"></span>
                        } @else {
                          <i class="bi bi-arrow-right me-1"></i>
                        }
                        Siguiente
                      </button>
                    </div>
                  </form>
                }

                <!-- ── Paso 3: Confirmación ── -->
                @case (3) {
                  @if (exitoso()) {
                    <div class="alert alert-success text-center">
                      <i class="bi bi-check-circle-fill fs-2 d-block mb-2"></i>
                      <strong>¡Registro completado!</strong>
                      <p class="mb-2">
                        El asesor <strong>{{ documentoRegistrado() || contacto().numero_documento }}</strong> fue registrado
                        exitosamente.
                      </p>
                      <button type="button" class="btn btn-success" (click)="verLista()">
                        <i class="bi bi-list-ul me-1"></i>Ver lista de asesores
                      </button>
                    </div>
                  } @else {
                    <h6 class="mb-3 text-muted">Datos de perfil de contacto</h6>
                    <div class="registro-resumen">
                      @for (fila of resumen(); track fila[0]) {
                        <div class="registro-resumen__row">
                          <span class="registro-resumen__label">{{ fila[0] }}</span>
                          <span class="registro-resumen__value">{{ fila[1] || '—' }}</span>
                        </div>
                      }
                    </div>
                    <div class="wizard-nav mt-4">
                      <button type="button" class="btn btn-outline-secondary" (click)="step.set(2)">
                        <i class="bi bi-arrow-left me-1"></i>Anterior
                      </button>
                      <button type="button" class="btn btn-danger" (click)="handleFinalizar()" [disabled]="isBusy()">
                        @if (finalizarMut.isPending()) {
                          <span class="spinner-border spinner-border-sm me-1"></span>
                        } @else {
                          <i class="bi bi-check-circle me-1"></i>
                        }
                        Finalizar Registro
                      </button>
                    </div>
                  }
                }
              }
            }
          }
        </div>
      </div>

      <app-confirm-modal
        [show]="cuentaObjetivo() !== null"
        title="Deshabilitar cuenta de acceso"
        confirmLabel="Deshabilitar"
        confirmIcon="bi-person-fill-slash"
        confirmVariant="danger"
        [loading]="cambiarCuentaMut.isPending()"
        loadingLabel="Deshabilitando…"
        (confirm)="confirmarDeshabilitarCuenta()"
        (hide)="cuentaObjetivo.set(null)"
      >
        @if (cuentaObjetivo(); as obj) {
          ¿Confirma deshabilitar la cuenta de acceso de <strong>{{ obj.nombre }}</strong>?
          <br />
          <small class="text-muted">
            El comisionista no podrá iniciar sesión hasta que sea habilitado de nuevo por un administrador.
          </small>
        }
      </app-confirm-modal>
    </div>
  `,
})
export class AsesorConsumoPageComponent {
  private readonly api = inject(ApiClient);
  private readonly asesorApi = inject(AsesorConsumoApi);

  protected readonly pasos = PASOS;
  protected readonly tiposDoc = TIPOS_DOC;
  protected readonly generos = GENEROS;
  protected readonly leer = leerInput;
  protected readonly soloDigitos = soloDigitos;

  protected readonly tab = signal<Tab>('lista');
  protected readonly page = signal<number>(1);
  protected readonly size = signal<number>(10);
  protected readonly searchTipoDoc = signal<string>('');
  protected readonly searchDocumento = signal<string>('');
  protected readonly filtrosActivos = signal<boolean>(false);
  private readonly filtrosQuery = signal<AsesorConsumoFiltros | undefined>(undefined);
  protected readonly documentoEditar = signal<string | null>(null);
  private readonly editTrigger = signal<number>(0);
  protected readonly formReady = signal<boolean>(false);
  protected readonly step = signal<WizardStep>(1);
  protected readonly contacto = signal<FormContacto>(initContacto);
  protected readonly emocional = signal<FormEmocional>(INIT_EMOCIONAL);
  private readonly selectedDid = signal<number | null>(null);
  protected readonly error = signal<string>('');
  protected readonly exitoso = signal<boolean>(false);
  protected readonly documentoRegistrado = signal<string>('');
  // AP-0001: deshabilitar la cuenta de acceso del comisionista (distinto del estado de registro).
  protected readonly cuentaObjetivo = signal<{ doc: string; nombre: string } | null>(null);
  protected readonly cuentaMsg = signal<string>('');
  protected readonly cambiarCuentaMut = injectCambiarEstadoComisionista();

  protected readonly lista = injectAsesorConsumoList(
    () => this.page(),
    () => this.size(),
    () => this.filtrosQuery(),
  );
  protected readonly detalle = injectDetalleAsesorConsumo(() => this.documentoEditar());
  protected readonly subprogramas = injectSubprogramasConsumo(() => PROGRAMA_CONSUMO_ID);
  protected readonly paso1Mut = injectWizardPaso1Consumo();
  protected readonly paso3Mut = injectWizardPaso3Consumo();
  protected readonly finalizarMut = injectFinalizarConsumo();

  private readonly departamentosQ = injectQuery(() => ({
    queryKey: ['departamentos'],
    queryFn: () => this.api.get<Departamento[]>('/ubicaciones/departamentos').then((r) => r.data),
  }));

  private readonly ciudadesQ = injectQuery(() => {
    const did = this.selectedDid();
    return {
      queryKey: ['ciudades', did],
      queryFn: () => this.api.get<Ciudad[]>(`/ubicaciones/ciudades/${did}`).then((r) => r.data),
      enabled: !!did,
    };
  });

  private readonly canalesQ = injectQuery(() => {
    const cspid = this.contacto().comisionista_subprograma_id;
    return {
      queryKey: ['canales-consumo', cspid],
      queryFn: () =>
        this.api
          .get<Canal[]>(`/referencias/canales?cpid=${PROGRAMA_CONSUMO_ID}&cspid=${cspid}`)
          .then((r) => r.data),
      enabled: cspid !== '',
    };
  });

  private readonly oficinasQ = injectQuery(() => {
    const { cod_canales, comisionista_subprograma_id } = this.contacto();
    return {
      queryKey: ['oficinas-canal', cod_canales, comisionista_subprograma_id],
      queryFn: () =>
        this.api
          .get<Oficina[]>(`/referencias/oficinas?cod_canales=${cod_canales}&cspid=${comisionista_subprograma_id}`)
          .then((r) => r.data),
      enabled: cod_canales !== '',
    };
  });

  private readonly profesionesQ = injectQuery(() => ({
    queryKey: ['profesiones'],
    queryFn: () => this.api.get<{ tid: number; nombre: string }[]>('/referencias/profesiones').then((r) => r.data),
  }));

  protected readonly depOpts = computed<OpcionBuscador[]>(() =>
    (this.departamentosQ.data() ?? []).map((d) => ({ value: String(d.did), text: d.departamento })),
  );
  protected readonly ciudadOpts = computed<OpcionBuscador[]>(() =>
    (this.ciudadesQ.data() ?? []).map((c) => ({ value: String(c.cid), text: c.ciudad })),
  );
  protected readonly canalOpts = computed<OpcionBuscador[]>(() =>
    (this.canalesQ.data() ?? []).map((c) => ({ value: String(c.cod_canales), text: c.nom_canales })),
  );
  protected readonly oficinaOpts = computed<OpcionBuscador[]>(() =>
    (this.oficinasQ.data() ?? [])
      .filter((o) => o.nom_oficinas?.trim())
      .map((o) => ({ value: String(o.cod_oficinas), text: o.nom_oficinas as string })),
  );
  protected readonly profesionOpts = computed<OpcionBuscador[]>(() =>
    (this.profesionesQ.data() ?? []).map((p) => ({ value: String(p.tid), text: p.nombre })),
  );
  protected readonly placeholderOficina = computed<string>(() => {
    if (this.contacto().cod_canales === '') return 'Seleccione un canal primero';
    return this.oficinaOpts().length === 0 ? 'Sin oficinas disponibles' : 'Seleccione oficina...';
  });

  protected readonly isBusy = computed<boolean>(
    () => this.paso1Mut.isPending() || this.paso3Mut.isPending() || this.finalizarMut.isPending(),
  );

  protected readonly resumen = computed<[string, string][]>(() => {
    const contacto = this.contacto();
    return [
      ['Tipo Documento', etiquetaTipoDoc(contacto.tipo_documento)],
      ['Número Documento', this.documentoRegistrado() || contacto.numero_documento],
      ['Nombre Completo', contacto.nombre_completo],
      ['Género', dash(contacto.genero)],
      ['Fecha de Nacimiento', dash(contacto.fecha_nacimiento)],
      ['Celular', contacto.celular],
      ['Teléfono', dash(contacto.telefono)],
      ['Correo Electrónico', dash(contacto.email)],
      ['Dirección', dash(contacto.direccion)],
      ['Departamento', nombreEn(this.departamentosQ.data(), (d) => String(d.did) === contacto.departamento, (d) => d.departamento)],
      ['Ciudad', nombreEn(this.ciudadesQ.data(), (c) => String(c.cid) === contacto.ciudad, (c) => c.ciudad)],
      ['Programa', 'Consumo y Servicios'],
      [
        'Subprograma',
        nombreEn(this.subprogramas.data(), (s) => s.cspid === contacto.comisionista_subprograma_id, (s) => s.cspid_nombre),
      ],
      ['Canal', nombreEn(this.canalesQ.data(), (c) => String(c.cod_canales) === String(contacto.cod_canales), (c) => c.nom_canales)],
      [
        'Oficina',
        nombreEn(this.oficinasQ.data(), (o) => String(o.cod_oficinas) === String(contacto.cod_oficinas), (o) => o.nom_oficinas),
      ],
      ['Estado', etiquetaEstado(contacto.estado)],
      ['Firma Contrato', etiquetaFirma(contacto.firma_contrato)],
      ['Incentivos', contacto.incentivos ? 'Sí' : 'No'],
      ['Habeas Data', contacto.acepto_habeas_data ? 'Aceptado' : 'No aceptado'],
    ];
  });

  constructor() {
    // Carga el detalle en el formulario al editar un asesor.
    effect(() => {
      const data = this.detalle.data();
      const documentoEditar = this.documentoEditar();
      this.editTrigger();
      if (!data || !documentoEditar) return;
      untracked(() => {
        const contactoRaw = data.contacto;
        const emocionalRaw = data.emocional;
        if (contactoRaw) {
          const { form, selectedDid } = mapearContactoConsumoReg(contactoRaw, documentoEditar);
          if (selectedDid) this.selectedDid.set(selectedDid);
          this.contacto.set(form);
          this.formReady.set(true);
        }
        if (emocionalRaw) this.emocional.set(mapearEmocional(emocionalRaw));
      });
    });
  }

  protected patchC(cambios: Partial<FormContacto>): void {
    this.contacto.update((prev) => ({ ...prev, ...cambios }));
  }

  protected setSize(n: number): void {
    this.size.set(n);
    this.page.set(1);
  }

  protected onDepartamento(value: string): void {
    if (value === this.contacto().departamento) return;
    this.selectedDid.set(Number(value) || null);
    this.patchC({ departamento: value, ciudad: '' });
  }

  protected onSubprograma(value: string): void {
    this.patchC({ comisionista_subprograma_id: Number(value), cod_canales: '', cod_oficinas: '' });
  }

  protected onCanal(value: string): void {
    const actual = this.contacto().cod_canales;
    if (value === (actual === '' ? '' : String(actual))) return;
    this.patchC({ cod_canales: value !== '' ? Number(value) : '', cod_oficinas: '' });
  }

  protected handleBuscar(): void {
    const f: AsesorConsumoFiltros = {};
    if (this.searchTipoDoc()) f.tipo_doc = this.searchTipoDoc();
    if (this.searchDocumento()) f.documento = this.searchDocumento();
    this.filtrosQuery.set(f);
    this.filtrosActivos.set(true);
    this.page.set(1);
  }

  protected handleLimpiar(): void {
    this.searchTipoDoc.set('');
    this.searchDocumento.set('');
    this.filtrosQuery.set(undefined);
    this.filtrosActivos.set(false);
    this.page.set(1);
  }

  protected abrirEdicion(documento: string): void {
    this.formReady.set(false);
    this.editTrigger.update((prev) => prev + 1);
    this.contacto.set({ ...initContacto, numero_documento: documento });
    this.emocional.set(INIT_EMOCIONAL);
    this.step.set(1);
    this.error.set('');
    this.exitoso.set(false);
    this.tab.set('registro');
    if (documento === this.documentoEditar()) {
      void this.detalle.refetch();
    } else {
      this.documentoEditar.set(documento);
    }
  }

  protected nuevoRegistro(): void {
    this.formReady.set(true);
    this.documentoEditar.set(null);
    this.contacto.set(initContacto);
    this.emocional.set(INIT_EMOCIONAL);
    this.step.set(1);
    this.error.set('');
    this.exitoso.set(false);
    this.tab.set('registro');
  }

  protected verLista(): void {
    this.documentoEditar.set(null);
    this.contacto.set(initContacto);
    this.emocional.set(INIT_EMOCIONAL);
    this.step.set(1);
    this.exitoso.set(false);
    this.tab.set('lista');
  }

  protected async handlePaso1(e: Event): Promise<void> {
    e.preventDefault();
    this.error.set('');
    const contacto: FormContacto = this.contacto();
    if (!contacto.acepto_habeas_data) {
      this.error.set('Debe aceptar el habeas data');
      return;
    }
    if (contacto.estado === null) {
      this.error.set('Debe seleccionar el estado del asesor');
      return;
    }
    if (!this.documentoEditar()) {
      try {
        const check = await this.asesorApi.verificar(contacto.numero_documento);
        if (check.registrado) {
          this.error.set(`El asesor con ${contacto.tipo_documento} ${contacto.numero_documento} ya está registrado`);
          return;
        }
      } catch {
        this.error.set('No se pudo verificar el documento. Intente de nuevo.');
        return;
      }
    }
    try {
      const result = await this.paso1Mut.mutateAsync({
        numero_documento: contacto.numero_documento,
        tipo_documento: contacto.tipo_documento,
        nombre_completo: contacto.nombre_completo,
        genero: contacto.genero,
        fecha_nacimiento: contacto.fecha_nacimiento,
        celular: contacto.celular,
        telefono: contacto.telefono || null,
        email: contacto.email || null,
        direccion: contacto.direccion,
        departamento: contacto.departamento,
        ciudad: contacto.ciudad,
        comisionista_programa_id: PROGRAMA_CONSUMO_ID,
        comisionista_subprograma_id: Number(contacto.comisionista_subprograma_id),
        cod_canales: contacto.cod_canales !== '' ? Number(contacto.cod_canales) : null,
        cod_oficinas: contacto.cod_oficinas !== '' ? Number(contacto.cod_oficinas) : null,
        acepto_habeas_data: 1,
        incentivos: contacto.incentivos,
        estado: contacto.estado,
        firma_contrato: contacto.firma_contrato,
      });
      this.documentoRegistrado.set(result.numero_documento);
      this.step.set(2);
    } catch (err: unknown) {
      this.error.set(detalleError(err, 'Error en paso 1'));
    }
  }

  protected async handlePaso3(e: Event): Promise<void> {
    e.preventDefault();
    this.error.set('');
    const emocional: FormEmocional = this.emocional();
    if (!emocional.acepto_terminos_y_condiciones) {
      this.error.set('Debe aceptar los términos y condiciones');
      return;
    }
    try {
      await this.paso3Mut.mutateAsync(
        payloadEmocional(
          emocional,
          this.documentoRegistrado() || this.contacto().numero_documento,
          PROGRAMA_CONSUMO_ID,
        ),
      );
      this.step.set(3);
    } catch (err: unknown) {
      this.error.set(detalleError(err, 'Error en paso 3'));
    }
  }

  protected async handleFinalizar(): Promise<void> {
    this.error.set('');
    try {
      await this.finalizarMut.mutateAsync(this.documentoRegistrado() || this.contacto().numero_documento);
      this.exitoso.set(true);
      void this.lista.refetch();
    } catch (err: unknown) {
      this.error.set(detalleError(err, 'Error al finalizar'));
    }
  }

  protected async confirmarDeshabilitarCuenta(): Promise<void> {
    const objetivo = this.cuentaObjetivo();
    if (!objetivo) return;
    try {
      await this.cambiarCuentaMut.mutateAsync({
        programa: 'consumo',
        numeroDocumento: objetivo.doc,
        payload: { activo: false },
      });
      this.cuentaMsg.set(`Cuenta de acceso de ${objetivo.nombre} deshabilitada`);
      this.cuentaObjetivo.set(null);
    } catch (err: unknown) {
      this.error.set(detalleError(err, 'No se pudo deshabilitar la cuenta'));
      this.cuentaObjetivo.set(null);
    }
  }
}
