import { ChangeDetectionStrategy, Component, computed, effect, inject, signal, untracked } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../shared/api/client';
import { AuthStore } from '../../entities/user/model/authStore';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { EstadoSwitchComponent } from '../../shared/ui/components/estado-switch.component';
import {
  TomSelectBuscadorComponent,
  type OpcionBuscador,
} from '../../shared/ui/components/tom-select-buscador.component';
import { PerfilEmocionalCamposComponent } from '../../widgets/perfil-emocional/perfil-emocional-campos.component';
import {
  INIT_EMOCIONAL,
  payloadEmocional,
  type FormEmocional,
} from '../../widgets/perfil-emocional/perfil-emocional';
import {
  injectDetalleAsesorConsumo,
  injectSubprogramasConsumo,
  injectWizardPaso1Consumo,
  injectWizardPaso3Consumo,
} from '../../features/asesor-consumo/model/queries';
import { leerInput, soloDigitos } from '../../shared/lib/inputs';
import { refId, refObj, strDe } from '../../shared/lib/parseContacto';

const PROGRAMA_CONSUMO_ID = 2 as const;

type PerfilTab = 'contacto' | 'emocional';

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
  comisionista_subprograma_id: '',
  cod_canales: '',
  cod_oficinas: '',
  acepto_habeas_data: true,
  incentivos: false,
  estado: 1,
  firma_contrato: null,
};

const INIT_EMOCIONAL_PERFIL: FormEmocional = { ...INIT_EMOCIONAL, acepto_terminos_y_condiciones: true };

const GENERO_NOMBRE: Record<string, string> = {
  '0': 'Femenino',
  '1': 'Masculino',
  F: 'Femenino',
  M: 'Masculino',
  Femenino: 'Femenino',
  Masculino: 'Masculino',
  Otro: 'Otro',
  O: 'Otro',
};

function toJsonStr(v: unknown): string {
  if (Array.isArray(v)) return v.length === 0 ? '' : JSON.stringify(v);
  if (typeof v === 'string') return v;
  return '';
}

function parseTipoDocPerfil(raw: unknown): string {
  if (typeof raw === 'object' && raw !== null) {
    return (raw as Record<string, string>)['codigo'] ?? 'CC';
  }
  return typeof raw === 'string' ? raw : 'CC';
}

function parseGeneroPerfil(raw: unknown): string {
  if (typeof raw === 'object' && raw !== null) {
    return (raw as Record<string, string>)['nombre'] ?? '';
  }
  if (typeof raw === 'string') {
    return GENERO_NOMBRE[raw] ?? raw;
  }
  return '';
}

function parseEstadoPerfil(v: unknown): 0 | 1 | null {
  if (v === 1) return 1;
  if (v === 0) return 0;
  return null;
}

function mapearContactoConsumo(c: Record<string, unknown>): { form: FormContacto; selectedDid: number | null } {
  const depObj = refObj(c['departamento']);
  const ciuObj = refObj(c['ciudad']);
  const fechaNac: string = typeof c['fecha_nacimiento'] === 'string' ? c['fecha_nacimiento'].slice(0, 10) : '';
  const form: FormContacto = {
    numero_documento: strDe(c['numero_documento']),
    tipo_documento: parseTipoDocPerfil(c['tipo_documento']).replace(/\./g, ''),
    nombre_completo: strDe(c['nombre_completo']),
    genero: parseGeneroPerfil(c['genero']),
    fecha_nacimiento: fechaNac,
    celular: strDe(c['celular']),
    telefono: c['telefono'] ? String(c['telefono']) : '',
    email: c['email'] ? String(c['email']) : '',
    direccion: strDe(c['direccion']),
    departamento: depObj ? strDe(depObj['did']) : strDe(c['departamento']),
    ciudad: ciuObj ? strDe(ciuObj['cid']) : strDe(c['ciudad']),
    comisionista_subprograma_id: refId(c['comisionista_subprograma_id'], 'cspid'),
    cod_canales: refId(c['cod_canales'], 'cod_canales'),
    cod_oficinas: refId(c['cod_oficinas'], 'cod_oficinas'),
    acepto_habeas_data: Boolean(c['acepto_habeas_data']),
    incentivos: Boolean(c['incentivos']),
    estado: parseEstadoPerfil(c['estado']),
    firma_contrato: c['firma_contrato'] !== undefined && c['firma_contrato'] !== null ? Boolean(c['firma_contrato']) : null,
  };
  const did = refId(c['departamento'], 'did');
  return { form, selectedDid: typeof did === 'number' ? did : null };
}

function mapearEmocionalConsumo(e: Record<string, unknown>): FormEmocional {
  return {
    con_quien_vives: toJsonStr(e['con_quien_vives']),
    estado_civil: String(e['estado_civil'] ?? ''),
    numero_hijos: e['numero_hijos'] != null ? String(e['numero_hijos']) : '',
    info_hijos: String(e['info_hijos'] ?? ''),
    hobbies: toJsonStr(e['hobbies']),
    nivel_educativo: String(e['nivel_educativo'] ?? ''),
    profesion: String(e['profesion'] ?? ''),
    temas_a_profundizar: toJsonStr(e['temas_a_profundizar']),
    premios_gustaria_recibir: toJsonStr(e['premios_gustaria_recibir']),
    propositos_familiares: toJsonStr(e['propositos_familiares']),
    propositos_financieros: toJsonStr(e['propositos_financieros']),
    propositos_diversion: toJsonStr(e['propositos_diversion']),
    propositos_salud: toJsonStr(e['propositos_salud']),
    propositos_competencias: toJsonStr(e['propositos_competencias']),
    numero_mascotas: e['numero_mascotas'] != null ? String(e['numero_mascotas']) : '',
    info_mascotas: String(e['info_mascotas'] ?? ''),
    acepto_terminos_y_condiciones: Boolean(e['acepto_terminos_y_condiciones'] ?? true),
  };
}

function detalleError(err: unknown, fallback: string): string {
  const msg = (err as { response?: { data?: { detail?: string | string[] } } })?.response?.data?.detail;
  return Array.isArray(msg) ? msg.join(' | ') : (msg ?? fallback);
}

@Component({
  selector: 'app-perfil-consumo-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, EstadoSwitchComponent, TomSelectBuscadorComponent, PerfilEmocionalCamposComponent],
  template: `
    <div>
      <app-page-header
        title="Mi Perfil — Comisionista Consumo"
        subtitle="Edita tus datos de contacto y tu perfil emocional"
        icon="bi-person-circle"
      />

      <div class="card shadow-sm" style="border: none">
        <div class="card-header bg-white border-0 pt-3">
          <ul class="nav nav-tabs">
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'contacto'" (click)="tab.set('contacto')">
                <i class="bi bi-person me-2"></i>Contacto
              </button>
            </li>
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'emocional'" (click)="tab.set('emocional')">
                <i class="bi bi-heart me-2"></i>Perfil Emocional
              </button>
            </li>
          </ul>
        </div>
        <div class="card-body p-4">
          @if (cargando()) {
            <div class="text-center py-5"><div class="spinner-border text-danger" role="status"></div></div>
          } @else {
            @if (error()) {
              <div class="alert alert-danger alert-dismissible">
                {{ error() }}
                <button type="button" class="btn-close" aria-label="Close" (click)="error.set('')"></button>
              </div>
            }
            @if (okMsg()) {
              <div class="alert alert-success alert-dismissible">
                {{ okMsg() }}
                <button type="button" class="btn-close" aria-label="Close" (click)="okMsg.set('')"></button>
              </div>
            }

            <!-- ── Tab: Contacto ── -->
            @if (tab() === 'contacto') {
              @let c = contacto();
              <form (submit)="handleGuardarContacto($event)">
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
                    <label class="form-label"><i class="bi bi-hash me-1 text-danger"></i>Número Documento</label>
                    <input class="form-control" [value]="c.numero_documento" disabled />
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
                    <app-tom-select-buscador [options]="depOpts()" [value]="c.departamento" [reabrirAlLimpiar]="false"
                      (valueChange)="onDepartamento($event)" placeholder="Seleccione departamento..." />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label"><i class="bi bi-pin-map me-1 text-danger"></i>Ciudad *</label>
                    <app-tom-select-buscador [options]="ciudadOpts()" [value]="c.ciudad" [reabrirAlLimpiar]="false"
                      (valueChange)="onCiudad($event)"
                      [placeholder]="c.departamento ? 'Seleccione ciudad...' : 'Seleccione un departamento primero'"
                      [locked]="!c.departamento" />
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
                    <app-tom-select-buscador [options]="canalOpts()" [value]="c.cod_canales === '' ? '' : '' + c.cod_canales"
                      [reabrirAlLimpiar]="false" (valueChange)="onCanal($event)"
                      [placeholder]="canalOpts().length === 0 ? 'Sin canales disponibles' : 'Seleccione canal...'"
                      [locked]="canalOpts().length === 0" />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label"><i class="bi bi-building me-1 text-danger"></i>Oficina</label>
                    <app-tom-select-buscador [options]="oficinaOpts()"
                      [value]="c.cod_oficinas === '' ? '' : '' + c.cod_oficinas" [reabrirAlLimpiar]="false"
                      (valueChange)="patchC({ cod_oficinas: $event !== '' ? +$event : '' })"
                      [placeholder]="placeholderOficina()"
                      [disabled]="!(c.cod_canales !== '' && oficinaOpts().length > 0)" />
                  </div>
                  <div class="col-12 col-md-6">
                    <div>
                      <app-estado-switch id="perfil-consumo-estado" [checked]="c.estado === 1"
                        (checkedChange)="patchC({ estado: $event ? 1 : 0 })" [disabled]="true" />
                    </div>
                  </div>
                  <div class="col-12">
                    <label class="form-label"><i class="bi bi-file-earmark-check me-1 text-danger"></i>Firma de Contrato</label>
                    <div class="d-flex gap-4 flex-wrap">
                      <div class="form-check">
                        <input class="form-check-input" type="radio" id="perfil-firma-contrato-si" name="firma_contrato"
                          [checked]="c.firma_contrato === true" (change)="patchC({ firma_contrato: true })" />
                        <label class="form-check-label" for="perfil-firma-contrato-si">El contrato fue firmado</label>
                      </div>
                      <div class="form-check">
                        <input class="form-check-input" type="radio" id="perfil-firma-contrato-no" name="firma_contrato"
                          [checked]="c.firma_contrato === false" (change)="patchC({ firma_contrato: false })" />
                        <label class="form-check-label" for="perfil-firma-contrato-no">No requiere firma de Contrato</label>
                      </div>
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="form-check">
                      <input class="form-check-input" type="checkbox" id="perfil-habeas-data-consumo"
                        [checked]="c.acepto_habeas_data" (change)="patchC({ acepto_habeas_data: $any($event.target).checked })" />
                      <label class="form-check-label" for="perfil-habeas-data-consumo">
                        Acepto el tratamiento de datos personales (Habeas Data) *
                      </label>
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="form-check">
                      <input class="form-check-input" type="checkbox" id="perfil-incentivos-consumo" [checked]="c.incentivos"
                        (change)="patchC({ incentivos: $any($event.target).checked })" disabled />
                      <label class="form-check-label" for="perfil-incentivos-consumo">Tiene Incentivos</label>
                    </div>
                  </div>
                </div>
                <div class="d-flex justify-content-end mt-4">
                  <button type="submit" class="btn btn-danger" [disabled]="isBusy()">
                    @if (guardarContacto.isPending()) {
                      <span class="spinner-border spinner-border-sm me-2"></span>
                    } @else {
                      <i class="bi bi-check-circle me-2"></i>
                    }
                    Guardar
                  </button>
                </div>
              </form>
            }

            <!-- ── Tab: Perfil Emocional ── -->
            @if (tab() === 'emocional') {
              <form (submit)="handleGuardarEmocional($event)">
                <h6 class="mb-3 fw-semibold text-danger">
                  <i class="bi bi-emoji-smile me-2"></i>Perfil Emocional
                </h6>
                <app-perfil-emocional-campos
                  [(emocional)]="emocional"
                  [profesiones]="profesionOpts()"
                  persona="segunda"
                  terminosId="perfil-terminos-consumo"
                  [profesionSimple]="true"
                />
                <div class="d-flex justify-content-end mt-4">
                  <button type="submit" class="btn btn-danger" [disabled]="isBusy()">
                    @if (guardarEmocional.isPending()) {
                      <span class="spinner-border spinner-border-sm me-2"></span>
                    } @else {
                      <i class="bi bi-check-circle me-2"></i>
                    }
                    Guardar
                  </button>
                </div>
              </form>
            }
          }
        </div>
      </div>
    </div>
  `,
})
export class PerfilConsumoPageComponent {
  private readonly api = inject(ApiClient);
  private readonly auth = inject(AuthStore);

  protected readonly tiposDoc = TIPOS_DOC;
  protected readonly generos = GENEROS;
  protected readonly leer = leerInput;
  protected readonly soloDigitos = soloDigitos;

  protected readonly tab = signal<PerfilTab>('contacto');
  protected readonly contacto = signal<FormContacto>(initContacto);
  protected readonly emocional = signal<FormEmocional>(INIT_EMOCIONAL_PERFIL);
  private readonly selectedDid = signal<number | null>(null);
  protected readonly error = signal<string>('');
  protected readonly okMsg = signal<string>('');
  private readonly datosListos = signal<boolean>(false);

  private readonly miDocumento = computed<string | null>(() => this.auth.user()?.username ?? null);
  private readonly detalle = injectDetalleAsesorConsumo(() => this.miDocumento());
  protected readonly guardarContacto = injectWizardPaso1Consumo();
  protected readonly guardarEmocional = injectWizardPaso3Consumo();
  protected readonly subprogramas = injectSubprogramasConsumo(() => PROGRAMA_CONSUMO_ID);

  private readonly departamentosQ = injectQuery(() => ({
    queryKey: ['departamentos'],
    queryFn: () =>
      this.api.get<{ did: number; departamento: string }[]>('/ubicaciones/departamentos').then((r) => r.data),
  }));
  private readonly ciudadesQ = injectQuery(() => {
    const did = this.selectedDid();
    return {
      queryKey: ['ciudades', did],
      queryFn: () => this.api.get<{ cid: number; ciudad: string }[]>(`/ubicaciones/ciudades/${did}`).then((r) => r.data),
      enabled: !!did,
    };
  });
  private readonly canalesQ = injectQuery(() => {
    const cspid = this.contacto().comisionista_subprograma_id;
    return {
      queryKey: ['canales-consumo', cspid],
      queryFn: () =>
        this.api
          .get<{ cod_canales: number; nom_canales: string; cpid: number; cspid: number }[]>(
            `/referencias/canales?cpid=${PROGRAMA_CONSUMO_ID}&cspid=${cspid}`,
          )
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
          .get<{ cod_oficinas: number; nom_oficinas: string | null }[]>(
            `/referencias/oficinas?cod_canales=${cod_canales}&cspid=${comisionista_subprograma_id}`,
          )
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
    () => this.guardarContacto.isPending() || this.guardarEmocional.isPending(),
  );
  // No se incluye isFetching: en un refetch (tras guardar) el formulario sigue montado
  // para que los Tom Select conserven su selección.
  protected readonly cargando = computed<boolean>(() => !this.datosListos() || this.detalle.isLoading());

  constructor() {
    // ── Cargar datos del usuario logueado ──
    effect(() => {
      const data = this.detalle.data();
      if (!data) return;
      untracked(() => {
        const contactoData = data.contacto;
        if (!contactoData) {
          this.datosListos.set(true);
          return;
        }
        const { form, selectedDid } = mapearContactoConsumo(contactoData);
        if (selectedDid) this.selectedDid.set(selectedDid);
        this.contacto.set(form);
        this.datosListos.set(true);
      });
    });

    effect(() => {
      const emocionalData = this.detalle.data()?.emocional;
      if (!emocionalData) return;
      untracked(() => this.emocional.set(mapearEmocionalConsumo(emocionalData)));
    });

    effect((onCleanup) => {
      if (!this.okMsg()) return;
      const id = setTimeout(() => this.okMsg.set(''), 10_000);
      onCleanup(() => clearTimeout(id));
    });
    effect((onCleanup) => {
      if (!this.error()) return;
      const id = setTimeout(() => this.error.set(''), 10_000);
      onCleanup(() => clearTimeout(id));
    });
  }

  protected patchC(cambios: Partial<FormContacto>): void {
    this.contacto.update((prev) => ({ ...prev, ...cambios }));
  }

  protected onDepartamento(value: string): void {
    // Solo limpiar ciudad si el departamento REALMENTE cambió.
    if (this.contacto().departamento === value) return;
    this.selectedDid.set(Number(value) || null);
    this.patchC({ departamento: value, ciudad: '' });
  }

  protected onCiudad(value: string): void {
    if (this.contacto().ciudad === value) return;
    this.patchC({ ciudad: value });
  }

  protected onSubprograma(value: string): void {
    this.patchC({
      comisionista_subprograma_id: value === '' ? '' : Number(value),
      cod_canales: '',
      cod_oficinas: '',
    });
  }

  protected onCanal(value: string): void {
    this.patchC({ cod_canales: value !== '' ? Number(value) : '', cod_oficinas: '' });
  }

  protected async handleGuardarContacto(e: Event): Promise<void> {
    e.preventDefault();
    this.error.set('');
    this.okMsg.set('');
    const contacto: FormContacto = this.contacto();
    if (!contacto.departamento) {
      this.error.set('Debe seleccionar un Departamento');
      return;
    }
    if (!contacto.ciudad) {
      this.error.set('Debe seleccionar una ciudad');
      return;
    }
    if (!contacto.acepto_habeas_data) {
      this.error.set('Debe aceptar el habeas data');
      return;
    }
    if (contacto.estado === null) {
      this.error.set('Debe seleccionar el estado del asesor');
      return;
    }
    try {
      const result = await this.guardarContacto.mutateAsync({
        numero_documento: contacto.numero_documento || this.miDocumento(),
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
      this.okMsg.set('Datos de contacto guardados.');
      if (result?.numero_documento) void this.detalle.refetch();
    } catch (err: unknown) {
      this.error.set(detalleError(err, 'Error en paso 1'));
    }
  }

  protected async handleGuardarEmocional(e: Event): Promise<void> {
    e.preventDefault();
    this.error.set('');
    this.okMsg.set('');
    const emocional: FormEmocional = this.emocional();
    if (!emocional.acepto_terminos_y_condiciones) {
      this.error.set('Debe aceptar los términos y condiciones');
      return;
    }
    try {
      await this.guardarEmocional.mutateAsync(
        payloadEmocional(emocional, this.contacto().numero_documento || this.miDocumento(), PROGRAMA_CONSUMO_ID),
      );
      this.okMsg.set('Perfil emocional guardado.');
      void this.detalle.refetch();
    } catch (err: unknown) {
      this.error.set(detalleError(err, 'Error en paso 3'));
    }
  }
}
