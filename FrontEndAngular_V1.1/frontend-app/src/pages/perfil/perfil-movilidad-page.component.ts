import { ChangeDetectionStrategy, Component, computed, effect, inject, signal, untracked } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
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
import { TributarioCamposComponent } from '../../widgets/tributario/tributario-campos.component';
import {
  INIT_TRIBUTARIO,
  documentosTributariosAEliminar,
  mapearTributario,
  parseTipoCuenta,
  payloadTributario,
  sincronizarComision,
  validarTributario,
  type DatosComision,
  type DocTributario,
  type FormTributario,
} from '../../widgets/tributario/tributario';
import { injectUploaderPropio } from '../../widgets/documentos-carga/documento-uploader';
import { injectMaxUploadBytes } from '../../features/config/model/uploadLimits';
import {
  injectGuardarMiContactoMovilidad,
  injectGuardarMiEmocionalMovilidad,
  injectGuardarMiTributarioMovilidad,
  injectMiDetalleMovilidad,
} from '../../features/perfil-self/model/miPerfilMovilidad';
import {
  fechaCorta,
  parseBoolOrNull,
  parseEstado,
  parseGenero,
  parseNumOrNull,
  parseTipoDoc,
  refId,
  refObj,
  strDe,
} from '../../shared/lib/parseContacto';
import { leerInput, soloDigitos } from '../../shared/lib/inputs';
import { MisDocumentosComponent } from './mis-documentos.component';

const PROGRAMA_MOVILIDAD_ID = 1;

type PerfilTab = 'contacto' | 'tributario' | 'emocional' | 'documentacion';

function tabFromHash(hash: string | null): PerfilTab | null {
  const clean: string = (hash || '').replace(/^#/, '').toLowerCase();
  if (clean === 'documentos' || clean === 'documentacion') return 'documentacion';
  if (clean === 'contacto') return 'contacto';
  if (clean === 'tributario') return 'tributario';
  if (clean === 'emocional') return 'emocional';
  return null;
}

const TIPOS_DOC: readonly string[] = ['CC', 'CE', 'F&I', 'GC', 'PEP', 'PPT', 'VDA'];
const GENEROS: readonly string[] = ['Masculino', 'Femenino', 'Otro'];

interface FormContacto extends DatosComision {
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
  cod_canales: '',
  cod_oficinas: '',
  acepto_habeas_data: true,
  incentivos: false,
  estado: 1,
  firma_contrato: null,
  banco: null,
  tipo_de_cuenta: '',
  numero_de_cuenta: '',
  numero_de_cuenta_verifica: '',
  requiere_comision: null,
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

function mapearContactoMovilidad(c: Record<string, unknown>): FormContacto {
  const depObj = refObj(c['departamento']);
  const ciuObj = refObj(c['ciudad']);
  const cuenta: string = strDe(c['numero_de_cuenta']);
  return {
    numero_documento: strDe(c['numero_documento']),
    tipo_documento: parseTipoDoc(c['tipo_documento']).replace(/\./g, ''),
    nombre_completo: strDe(c['nombre_completo']),
    genero: parseGenero(c['genero'], GENERO_NOMBRE),
    fecha_nacimiento: fechaCorta(c['fecha_nacimiento']),
    celular: strDe(c['celular']),
    telefono: c['telefono'] ? String(c['telefono']) : '',
    email: c['email'] ? String(c['email']) : '',
    direccion: strDe(c['direccion']),
    departamento: depObj ? strDe(depObj['did']) : strDe(c['departamento']),
    ciudad: ciuObj ? strDe(ciuObj['cid']) : strDe(c['ciudad']),
    cod_canales: refId(c['cod_canales'], 'cod_canales'),
    cod_oficinas: refId(c['cod_oficinas'], 'cod_oficinas'),
    acepto_habeas_data: Boolean(c['acepto_habeas_data']),
    incentivos: Boolean(c['incentivos']),
    estado: parseEstado(c['estado']),
    firma_contrato: parseBoolOrNull(c['firma_contrato']),
    requiere_comision: parseBoolOrNull(c['requiere_comision']),
    banco: parseNumOrNull(c['banco']),
    tipo_de_cuenta: parseTipoCuenta(c['tipo_de_cuenta']),
    numero_de_cuenta: cuenta,
    numero_de_cuenta_verifica: cuenta,
  };
}

function mapearEmocionalMovilidad(e: Record<string, unknown>): FormEmocional {
  return {
    con_quien_vives: strDe(e['con_quien_vives']),
    estado_civil: strDe(e['estado_civil']),
    numero_hijos: e['numero_hijos'] != null ? String(e['numero_hijos']) : '',
    info_hijos: strDe(e['info_hijos']),
    hobbies: strDe(e['hobbies']),
    nivel_educativo: strDe(e['nivel_educativo']),
    profesion: strDe(e['profesion']),
    temas_a_profundizar: strDe(e['temas_a_profundizar']),
    premios_gustaria_recibir: strDe(e['premios_gustaria_recibir']),
    propositos_familiares: strDe(e['propositos_familiares']),
    propositos_financieros: strDe(e['propositos_financieros']),
    propositos_diversion: strDe(e['propositos_diversion']),
    propositos_salud: strDe(e['propositos_salud']),
    propositos_competencias: strDe(e['propositos_competencias']),
    numero_mascotas: e['numero_mascotas'] != null ? String(e['numero_mascotas']) : '',
    info_mascotas: strDe(e['info_mascotas']),
    acepto_terminos_y_condiciones: Boolean(e['acepto_terminos_y_condiciones'] ?? true),
  };
}

function payloadContactoMovilidad(c: FormContacto, numero_documento: string | null): Record<string, unknown> {
  return {
    numero_documento,
    tipo_documento: c.tipo_documento,
    nombre_completo: c.nombre_completo,
    genero: c.genero,
    fecha_nacimiento: c.fecha_nacimiento,
    celular: c.celular,
    telefono: c.telefono || null,
    email: c.email || null,
    direccion: c.direccion,
    departamento: c.departamento,
    ciudad: c.ciudad,
    comisionista_programa_id: PROGRAMA_MOVILIDAD_ID,
    comisionista_subprograma_id: null,
    cod_canales: c.cod_canales !== '' ? Number(c.cod_canales) : null,
    cod_oficinas: c.cod_oficinas !== '' ? Number(c.cod_oficinas) : null,
    acepto_habeas_data: 1 as const,
    incentivos: c.incentivos,
    estado: c.estado as 0 | 1,
    firma_contrato: c.firma_contrato,
    banco: c.banco,
    tipo_de_cuenta: c.tipo_de_cuenta || null,
    numero_de_cuenta: c.numero_de_cuenta || null,
    requiere_comision: c.requiere_comision,
  };
}

function detalleError(err: unknown, fallback: string): string {
  const msg = (err as { response?: { data?: { detail?: string | string[] } } })?.response?.data?.detail;
  if (Array.isArray(msg)) return msg.join(' | ');
  if (typeof msg === 'string' && msg) return msg;
  if (err instanceof Error && err.message) return err.message;
  return fallback;
}

interface Catalogo {
  tid: number;
  nombre: string;
}

const aOpciones = (items: Catalogo[] | undefined): OpcionBuscador[] =>
  (items ?? []).map((o) => ({ value: String(o.tid), text: o.nombre }));

@Component({
  selector: 'app-perfil-movilidad-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    PageHeaderComponent,
    EstadoSwitchComponent,
    TomSelectBuscadorComponent,
    PerfilEmocionalCamposComponent,
    TributarioCamposComponent,
    MisDocumentosComponent,
  ],
  template: `
    <div>
      <app-page-header
        title="Mi Perfil — Comisionista Movilidad"
        subtitle="Edita tus datos de contacto, tributarios y emocionales"
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
              <button type="button" class="nav-link" [class.active]="tab() === 'tributario'" (click)="tab.set('tributario')">
                <i class="bi bi-bank me-2"></i>Tributario
              </button>
            </li>
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'emocional'" (click)="tab.set('emocional')">
                <i class="bi bi-heart me-2"></i>Perfil Emocional
              </button>
            </li>
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'documentacion'"
                (click)="tab.set('documentacion')">
                <i class="bi bi-folder2-open me-2"></i>Documentación
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

            @switch (tab()) {
              <!-- ── Tab: Contacto ── -->
              @case ('contacto') {
                @let c = contacto();
                <form (submit)="handleGuardarContacto($event)">
                  <h6 class="mb-3 fw-semibold text-danger">
                    <i class="bi bi-person-lines-fill me-2"></i>Información de Contacto
                  </h6>
                  <div class="row g-3">
                    <div class="col-md-4">
                      <label class="form-label"><i class="bi bi-person-badge me-1 text-danger"></i>Tipo Documento</label>
                      <select class="form-select" (change)="patchC({ tipo_documento: $any($event.target).value })">
                        @for (t of tiposDoc; track t) {
                          <option [value]="t" [selected]="t === c.tipo_documento">{{ t }}</option>
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
                    <div class="col-md-6">
                      <label class="form-label"><i class="bi bi-map me-1 text-danger"></i>Departamento *</label>
                      <app-tom-select-buscador [options]="depOpts()" [value]="c.departamento" [reabrirAlLimpiar]="false"
                        (valueChange)="onDepartamento($event)" placeholder="Seleccione departamento..." />
                    </div>
                    <div class="col-md-6">
                      <label class="form-label"><i class="bi bi-pin-map me-1 text-danger"></i>Ciudad *</label>
                      <app-tom-select-buscador [options]="ciudadOpts()" [value]="c.ciudad" [reabrirAlLimpiar]="false"
                        (valueChange)="onCiudad($event)"
                        [placeholder]="c.departamento ? 'Seleccione ciudad...' : 'Seleccione un departamento primero'"
                        [locked]="!c.departamento" />
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
                        (valueChange)="onOficina($event)" [placeholder]="placeholderOficina()"
                        [disabled]="!(c.cod_canales !== '' && oficinaOpts().length > 0)" />
                    </div>
                    <div class="col-12 col-md-6">
                      <div>
                        <app-estado-switch id="perfil-movilidad-estado" [checked]="c.estado === 1"
                          (checkedChange)="patchC({ estado: $event ? 1 : 0 })" [disabled]="true" />
                      </div>
                    </div>
                    <div class="col-12">
                      <label class="form-label"><i class="bi bi-file-earmark-check me-1 text-danger"></i>Firma de Contrato</label>
                      <div class="d-flex gap-4 flex-wrap">
                        <div class="form-check">
                          <input class="form-check-input" type="radio" id="perfil-mov-firma-si" name="firma_contrato-perfil-mov"
                            [checked]="c.firma_contrato === true" (change)="patchC({ firma_contrato: true })" />
                          <label class="form-check-label" for="perfil-mov-firma-si">El contrato fue firmado</label>
                        </div>
                        <div class="form-check">
                          <input class="form-check-input" type="radio" id="perfil-mov-firma-no" name="firma_contrato-perfil-mov"
                            [checked]="c.firma_contrato === false" (change)="patchC({ firma_contrato: false })" />
                          <label class="form-check-label" for="perfil-mov-firma-no">No requiere firma de Contrato</label>
                        </div>
                      </div>
                    </div>
                    <div class="col-12">
                      <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="perfil-mov-habeas-data" [checked]="c.acepto_habeas_data"
                          (change)="patchC({ acepto_habeas_data: $any($event.target).checked })" />
                        <label class="form-check-label" for="perfil-mov-habeas-data">
                          Acepto el tratamiento de datos personales (Habeas Data) *
                        </label>
                      </div>
                    </div>
                    <div class="col-12">
                      <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="perfil-mov-incentivos" [checked]="c.incentivos"
                          (change)="patchC({ incentivos: $any($event.target).checked })" disabled />
                        <label class="form-check-label" for="perfil-mov-incentivos">Tiene Incentivos</label>
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

              <!-- ── Tab: Tributario ── -->
              @case ('tributario') {
                <form (submit)="handleGuardarTributario($event)">
                  <h6 class="mb-3 fw-semibold text-danger">
                    <i class="bi bi-bank me-2"></i>Información Tributaria
                  </h6>
                  <app-tributario-campos
                    [tributario]="tributario()"
                    [contacto]="contacto()"
                    [docs]="misDocumentos.data()"
                    [uploader]="uploader"
                    [eps]="epsOpts()"
                    [afp]="afpOpts()"
                    [arl]="arlOpts()"
                    [bancos]="bancoOpts()"
                    prefijoId="perfil-mov-"
                    sufijoName="-perfil-mov"
                    preguntaComision="¿Trabajas con o sin comisión?"
                    [modoSimple]="true"
                    (tributarioChange)="patchT($event)"
                    (patchContacto)="patchC($event)"
                    (docsCambiaron)="refetchMisDocs()"
                    (uploadingChange)="docUploading.set($event)"
                  />
                  <div class="d-flex justify-content-end mt-4">
                    <button type="submit" class="btn btn-danger" [disabled]="isBusy() || docUploading()">
                      @if (guardarTributario.isPending()) {
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
              @case ('emocional') {
                <form (submit)="handleGuardarEmocional($event)">
                  <h6 class="mb-3 fw-semibold text-danger">
                    <i class="bi bi-emoji-smile me-2"></i>Perfil Emocional
                  </h6>
                  <app-perfil-emocional-campos
                    [(emocional)]="emocional"
                    [profesiones]="profesionOpts()"
                    persona="segunda"
                    terminosId="perfil-mov-terminos"
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

              <!-- ── Tab: Documentación ── -->
              @case ('documentacion') {
                <div>
                  <h6 class="mb-3 fw-semibold text-danger">
                    <i class="bi bi-folder2-open me-2"></i>Mis Documentos
                  </h6>
                  <p class="text-muted small mb-3">
                    Aquí puedes consultar y editar el nombre, estado y fecha de los documentos que has cargado. Para subir
                    nuevos archivos utiliza la pestaña Tributario.
                  </p>
                  @if (miDocumento()) {
                    <app-mis-documentos />
                  } @else {
                    <div class="alert alert-warning mb-0">No se pudo determinar tu número de documento.</div>
                  }
                </div>
              }
            }
          }
        </div>
      </div>
    </div>
  `,
})
export class PerfilMovilidadPageComponent {
  private readonly api = inject(ApiClient);
  private readonly auth = inject(AuthStore);
  private readonly fragment = toSignal(inject(ActivatedRoute).fragment, { initialValue: null });
  private readonly maxBytes = injectMaxUploadBytes();
  protected readonly uploader = injectUploaderPropio(() => this.maxBytes());

  protected readonly tiposDoc = TIPOS_DOC;
  protected readonly generos = GENEROS;
  protected readonly leer = leerInput;
  protected readonly soloDigitos = soloDigitos;

  protected readonly tab = signal<PerfilTab>('contacto');
  protected readonly contacto = signal<FormContacto>(initContacto);
  protected readonly tributario = signal<FormTributario>(INIT_TRIBUTARIO);
  protected readonly emocional = signal<FormEmocional>(INIT_EMOCIONAL_PERFIL);
  protected readonly error = signal<string>('');
  protected readonly okMsg = signal<string>('');
  private readonly datosListos = signal<boolean>(false);
  protected readonly docUploading = signal<boolean>(false);

  protected readonly miDocumento = computed<string | null>(() => this.auth.user()?.username ?? null);
  private readonly detalle = injectMiDetalleMovilidad();
  protected readonly guardarContacto = injectGuardarMiContactoMovilidad();
  protected readonly guardarTributario = injectGuardarMiTributarioMovilidad();
  protected readonly guardarEmocional = injectGuardarMiEmocionalMovilidad();

  private readonly selectedDid = computed<number | null>(() => {
    const dep: string = this.contacto().departamento;
    return dep ? Number(dep) : null;
  });

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
  private readonly canalesQ = injectQuery(() => ({
    queryKey: ['canales-movilidad'],
    queryFn: () =>
      this.api
        .get<{ cod_canales: number; nom_canales: string; cpid: number }[]>(
          `/referencias/canales?cpid=${PROGRAMA_MOVILIDAD_ID}`,
        )
        .then((r) => r.data),
  }));
  private readonly oficinasQ = injectQuery(() => {
    const cod = this.contacto().cod_canales;
    return {
      queryKey: ['oficinas-canal-movilidad', cod],
      queryFn: () =>
        this.api
          .get<{ cod_oficinas: number; nom_oficinas: string | null }[]>(`/referencias/oficinas?cod_canales=${cod}`)
          .then((r) => r.data),
      enabled: cod !== '',
    };
  });
  private readonly profesionesQ = injectQuery(() => ({
    queryKey: ['profesiones'],
    queryFn: () => this.api.get<Catalogo[]>('/referencias/profesiones').then((r) => r.data),
  }));
  private readonly epsQ = injectQuery(() => ({
    queryKey: ['eps-catalogo'],
    queryFn: () => this.api.get<Catalogo[]>('/referencias/eps').then((r) => r.data),
  }));
  private readonly afpQ = injectQuery(() => ({
    queryKey: ['afp-catalogo'],
    queryFn: () => this.api.get<Catalogo[]>('/referencias/afp').then((r) => r.data),
  }));
  private readonly arlQ = injectQuery(() => ({
    queryKey: ['arl-catalogo'],
    queryFn: () => this.api.get<Catalogo[]>('/referencias/arl').then((r) => r.data),
  }));
  private readonly bancosQ = injectQuery(() => ({
    queryKey: ['bancos-catalogo'],
    queryFn: () => this.api.get<Catalogo[]>('/referencias/bancos').then((r) => r.data),
  }));
  // AP-0055: los PDF propios se leen por /me/documentos (ownership por el JWT). El
  // endpoint /documentos/{doc} es de staff (DOCUMENTOS_MODERAR) y devolvia 403 al
  // comisionista, por lo que la pestana Tributario no mostraba ningun archivo.
  protected readonly misDocumentos = injectQuery(() => {
    const doc = this.miDocumento();
    return {
      queryKey: ['mis-documentos', doc],
      queryFn: () => this.api.get<(DocTributario & { estado: string })[]>('/me/documentos').then((r) => r.data),
      enabled: !!doc,
    };
  });

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
  protected readonly profesionOpts = computed<OpcionBuscador[]>(() => aOpciones(this.profesionesQ.data()));
  protected readonly epsOpts = computed<OpcionBuscador[]>(() => aOpciones(this.epsQ.data()));
  protected readonly afpOpts = computed<OpcionBuscador[]>(() => aOpciones(this.afpQ.data()));
  protected readonly arlOpts = computed<OpcionBuscador[]>(() => aOpciones(this.arlQ.data()));
  protected readonly bancoOpts = computed<OpcionBuscador[]>(() => aOpciones(this.bancosQ.data()));
  protected readonly placeholderOficina = computed<string>(() => {
    if (this.contacto().cod_canales === '') return 'Seleccione un canal primero';
    return this.oficinaOpts().length === 0 ? 'Sin oficinas disponibles' : 'Seleccione oficina...';
  });

  protected readonly isBusy = computed<boolean>(
    () => this.guardarContacto.isPending() || this.guardarTributario.isPending() || this.guardarEmocional.isPending(),
  );
  protected readonly cargando = computed<boolean>(() => !this.datosListos() || this.detalle.isLoading());

  constructor() {
    // La pestaña inicial (y los cambios posteriores) se toman del hash (#documentos, #tributario…).
    effect(() => {
      const next: PerfilTab | null = tabFromHash(this.fragment());
      if (next) untracked(() => this.tab.set(next));
    });

    // ── Carga de datos del usuario logueado ──
    effect(() => {
      const data = this.detalle.data();
      if (!data) return;
      untracked(() => {
        const contacto = data.contacto as Record<string, unknown> | null | undefined;
        if (!contacto) {
          this.datosListos.set(true);
          return;
        }
        this.contacto.set(mapearContactoMovilidad(contacto));
        this.datosListos.set(true);
      });
    });
    effect(() => {
      const tributario = this.detalle.data()?.tributario as Record<string, unknown> | null | undefined;
      if (!tributario) return;
      untracked(() => this.tributario.set(mapearTributario(tributario)));
    });
    effect(() => {
      const emocional = this.detalle.data()?.emocional as Record<string, unknown> | null | undefined;
      if (!emocional) return;
      untracked(() => this.emocional.set(mapearEmocionalMovilidad(emocional)));
    });

    sincronizarComision(this.contacto, this.tributario);

    // ── Auto-dismiss de mensajes ──
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

  protected patchT(cambios: Partial<FormTributario>): void {
    this.tributario.update((prev) => ({ ...prev, ...cambios }));
  }

  protected refetchMisDocs(): void {
    void this.misDocumentos.refetch();
  }

  protected onDepartamento(value: string): void {
    if (this.contacto().departamento === value) return;
    this.patchC({ departamento: value, ciudad: '' });
  }

  protected onCiudad(value: string): void {
    if (this.contacto().ciudad === value) return;
    this.patchC({ ciudad: value });
  }

  protected onCanal(value: string): void {
    const numVal: number | '' = value !== '' ? Number(value) : '';
    if (this.contacto().cod_canales === numVal) return;
    this.patchC({ cod_canales: numVal, cod_oficinas: '' });
  }

  protected onOficina(value: string): void {
    const numVal: number | '' = value !== '' ? Number(value) : '';
    if (this.contacto().cod_oficinas === numVal) return;
    this.patchC({ cod_oficinas: numVal });
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
      const result = await this.guardarContacto.mutateAsync(
        payloadContactoMovilidad(contacto, contacto.numero_documento || this.miDocumento()),
      );
      this.okMsg.set('Datos de contacto guardados.');
      if (result?.numero_documento) this.detalle.refetch();
    } catch (err: unknown) {
      this.error.set(detalleError(err, 'Error en paso 1'));
    }
  }

  protected async handleGuardarTributario(e: Event): Promise<void> {
    e.preventDefault();
    this.error.set('');
    this.okMsg.set('');
    const contacto: FormContacto = this.contacto();
    const tributario: FormTributario = this.tributario();
    const mensaje: string | null = validarTributario(contacto, tributario);
    if (mensaje) {
      this.error.set(mensaje);
      return;
    }
    const docNum: string | null = contacto.numero_documento || this.miDocumento();
    try {
      // Paso 1: re-guardar contacto para persistir requiere_comision/banco/cuenta antes del tributario
      await this.guardarContacto.mutateAsync(payloadContactoMovilidad(contacto, docNum));
      await this.guardarTributario.mutateAsync(payloadTributario(tributario, docNum));
      // Eliminar PDFs cuya entidad quedó en NO COMISION (alineado con AsesorMovilidadPage).
      const idsAEliminar: number[] = documentosTributariosAEliminar(tributario, this.misDocumentos.data());
      if (idsAEliminar.length > 0) {
        await Promise.all(idsAEliminar.map((id) => this.api.delete(`/me/documentos/${id}`)));
        void this.misDocumentos.refetch();
      }
      this.okMsg.set('Datos tributarios guardados.');
      this.detalle.refetch();
    } catch (err: unknown) {
      this.error.set(detalleError(err, 'Error en paso 2'));
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
        payloadEmocional(emocional, this.contacto().numero_documento || this.miDocumento(), PROGRAMA_MOVILIDAD_ID),
      );
      this.okMsg.set('Perfil emocional guardado.');
      this.detalle.refetch();
    } catch (err: unknown) {
      this.error.set(detalleError(err, 'Error en paso 3'));
    }
  }
}
