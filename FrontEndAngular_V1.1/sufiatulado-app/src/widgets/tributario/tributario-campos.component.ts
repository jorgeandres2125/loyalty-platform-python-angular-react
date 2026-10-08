import { ChangeDetectionStrategy, Component, computed, input, output } from '@angular/core';
import {
  TomSelectBuscadorComponent,
  type OpcionBuscador,
} from '../../shared/ui/components/tom-select-buscador.component';
import { DocZoneComponent } from '../documentos-carga/doc-zone.component';
import { CertificadoRowComponent } from '../documentos-carga/certificado-row.component';
import type { DocumentoUploader } from '../documentos-carga/documento-uploader';
import { leerInput, soloDigitos } from '../../shared/lib/inputs';
import {
  NO_COMISION_AFP,
  NO_COMISION_ARL,
  NO_COMISION_EPS,
  docPorTipo,
  type DatosComision,
  type DocTributario,
  type FormTributario,
} from './tributario';

interface Certificado {
  label: string;
  tipo: number;
  prefijo: string;
}

const CERTIFICADOS: readonly Certificado[] = [
  { label: 'Prepagada', tipo: 10, prefijo: 'PREPAGADA' },
  { label: 'Certificado intereses de vivienda', tipo: 11, prefijo: 'VIVIENDA' },
  { label: 'Dependientes', tipo: 14, prefijo: 'DEPENDIENTES' },
  { label: 'Pensión voluntaria', tipo: 12, prefijo: 'PENSIONVOL' },
  { label: 'AFC', tipo: 13, prefijo: 'AFC' },
];

const DOCUMENTOS_USUARIO: readonly Certificado[] = [
  { label: 'Fotocopia cédula de ciudadanía', tipo: 4, prefijo: 'CC' },
  { label: 'RUT', tipo: 5, prefijo: 'RUT' },
];

/**
 * Bloques 1–5 de la información tributaria (Movilidad): contratación, régimen de IVA,
 * EPS/AFP/ARL con su soporte PDF, información bancaria y certificados. Compartido por
 * el registro de asesores y el perfil propio del comisionista.
 */
@Component({
  selector: 'app-tributario-campos',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [TomSelectBuscadorComponent, DocZoneComponent, CertificadoRowComponent],
  template: `
    @let t = tributario();
    @let c = contacto();
    <div class="row g-3">
      <div class="col-12">
        <div class="border rounded p-3">
          <p class="mb-3" style="font-weight: 500">
            1. Para realizar su actividad de comisionista usted tuvo que contratar a más de una persona durante el último
            año por 6 meses o más?
          </p>
          <div class="d-flex gap-4">
            <div class="form-check">
              <input class="form-check-input" type="radio" [id]="prefijoId() + 'contratacion-no'"
                [name]="'contratacion_personal' + sufijoName()" [checked]="t.contratacion_personal === false"
                (change)="patchT({ contratacion_personal: false })" />
              <label class="form-check-label" [for]="prefijoId() + 'contratacion-no'">No</label>
            </div>
            <div class="form-check">
              <input class="form-check-input" type="radio" [id]="prefijoId() + 'contratacion-si'"
                [name]="'contratacion_personal' + sufijoName()" [checked]="t.contratacion_personal === true"
                (change)="patchT({ contratacion_personal: true })" />
              <label class="form-check-label" [for]="prefijoId() + 'contratacion-si'">Sí</label>
            </div>
          </div>
        </div>
      </div>
      <div class="col-12">
        <div class="border rounded p-3">
          <p class="mb-3" style="font-weight: 500">2. ¿A qué régimen de IVA pertenece?</p>
          <div class="d-flex gap-4">
            <div class="form-check">
              <input class="form-check-input" type="radio" [id]="prefijoId() + 'regimen-simplificado'"
                [name]="'regimen_iva' + sufijoName()" [checked]="t.regimen_iva === false"
                (change)="patchT({ regimen_iva: false })" />
              <label class="form-check-label" [for]="prefijoId() + 'regimen-simplificado'">
                No responsable de IVA (Simplificado)
              </label>
            </div>
            <div class="form-check">
              <input class="form-check-input" type="radio" [id]="prefijoId() + 'regimen-comun'"
                [name]="'regimen_iva' + sufijoName()" [checked]="t.regimen_iva === true"
                (change)="patchT({ regimen_iva: true })" />
              <label class="form-check-label" [for]="prefijoId() + 'regimen-comun'">Responsable de IVA (Común)</label>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Bloque EPS / AFP / ARL ── -->
      <div class="col-12">
        <div class="border rounded p-3">
          <p class="mb-3" style="font-weight: 500">
            3. Autorizo a la compañía CADENA SA, identificada con Nit 890.930.534-0 para que efectúe los descuentos
            correspondientes a los aportes en seguridad social, en salud, pensión y riesgos laborales y realice los pagos
            respectivos por cuenta mía a las siguientes entidades:
          </p>

          <!-- ── Con / Sin Comisión ── -->
          <div class="rounded p-2 mb-3"
            [class]="c.requiere_comision === null ? 'bg-warning-subtle border border-warning' : 'bg-light border'">
            <p class="mb-2 fw-semibold small">
              <i class="bi bi-toggles me-2"></i>{{ preguntaComision() }}
            </p>
            <div class="d-flex gap-4">
              <div class="form-check">
                <input class="form-check-input" type="radio" [id]="prefijoId() + 'comision-con'"
                  [name]="'requiere_comision' + sufijoName()" [checked]="c.requiere_comision === true"
                  (change)="patchContacto.emit({ requiere_comision: true })" />
                <label class="form-check-label" [for]="prefijoId() + 'comision-con'">Con Comisión</label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="radio" [id]="prefijoId() + 'comision-sin'"
                  [name]="'requiere_comision' + sufijoName()" [checked]="c.requiere_comision === false"
                  (change)="patchContacto.emit({ requiere_comision: false })" />
                <label class="form-check-label" [for]="prefijoId() + 'comision-sin'">Sin Comisión</label>
              </div>
            </div>
          </div>

          <!-- EPS -->
          <div class="mb-3">
            <label class="form-label fw-semibold">EPS</label>
            <app-doc-zone tipoLabel="EPS" tipoPrefix="EPS" [tipo]="7" [numeroDocumento]="c.numero_documento"
              [existingDoc]="doc(7)" [uploader]="uploader()" [disabled]="t.eps === null || t.eps === noComisionEps"
              (uploaded)="docsCambiaron.emit()" (deleted)="docsCambiaron.emit()" (uploadingChange)="uploadingChange.emit($event)">
              @if (epsOpts().length) {
                <app-tom-select-buscador [options]="epsOpts()" [value]="t.eps !== null ? '' + t.eps : ''"
                  (valueChange)="patchT({ eps: $event !== '' ? +$event : null })" placeholder="Seleccione EPS..."
                  [sinResultados]="!modoSimple()" [reabrirAlLimpiar]="!modoSimple()" [disabled]="c.requiere_comision === false" />
              } @else {
                <select class="form-select"></select>
              }
            </app-doc-zone>
          </div>

          <!-- AFP / Fondo de pensiones -->
          <div class="mb-3">
            <label class="form-label fw-semibold">Fondo de pensiones</label>
            <app-doc-zone tipoLabel="AFP" tipoPrefix="AFP" [tipo]="8" [numeroDocumento]="c.numero_documento"
              [existingDoc]="doc(8)" [uploader]="uploader()" [disabled]="t.afp === null || t.afp === noComisionAfp"
              (uploaded)="docsCambiaron.emit()" (deleted)="docsCambiaron.emit()" (uploadingChange)="uploadingChange.emit($event)">
              @if (afpOpts().length) {
                <app-tom-select-buscador [options]="afpOpts()" [value]="t.afp !== null ? '' + t.afp : ''"
                  (valueChange)="patchT({ afp: $event !== '' ? +$event : null })"
                  [placeholder]="modoSimple() ? 'Seleccione Fondo de pensiones...' : 'Seleccione AFP / Fondo de pensiones...'" [sinResultados]="!modoSimple()" [reabrirAlLimpiar]="!modoSimple()"
                  [disabled]="c.requiere_comision === false" />
              } @else {
                <select class="form-select"></select>
              }
            </app-doc-zone>
          </div>

          <!-- ARL -->
          <div class="mb-0">
            <label class="form-label fw-semibold">ARL</label>
            <app-doc-zone tipoLabel="ARL" tipoPrefix="ARL" [tipo]="9" [numeroDocumento]="c.numero_documento"
              [existingDoc]="doc(9)" [uploader]="uploader()" [disabled]="t.arl === null || t.arl === noComisionArl"
              (uploaded)="docsCambiaron.emit()" (deleted)="docsCambiaron.emit()" (uploadingChange)="uploadingChange.emit($event)">
              @if (arlOpts().length) {
                <app-tom-select-buscador [options]="arlOpts()" [value]="t.arl !== null ? '' + t.arl : ''"
                  (valueChange)="patchT({ arl: $event !== '' ? +$event : null })" placeholder="Seleccione ARL..."
                  [sinResultados]="!modoSimple()" [reabrirAlLimpiar]="!modoSimple()" [disabled]="c.requiere_comision === false" />
              } @else {
                <select class="form-select"></select>
              }
            </app-doc-zone>
          </div>
        </div>
      </div>

      <!-- ── Bloque Banco / Cuenta ── -->
      <div class="col-12">
        <div class="border rounded p-3">
          <p class="mb-3" style="font-weight: 500">4. Información bancaria para pago de comisiones:</p>

          <div class="mb-3">
            <label class="form-label fw-semibold">Banco</label>
            @if (bancoOpts().length) {
              <app-tom-select-buscador [options]="bancoOpts()" [value]="c.banco !== null ? '' + c.banco : ''"
                (valueChange)="patchContacto.emit({ banco: $event !== '' ? +$event : null })"
                placeholder="Seleccione banco..." [sinResultados]="!modoSimple()" [reabrirAlLimpiar]="!modoSimple()" />
            } @else {
              <select class="form-select"></select>
            }
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold">Tipo de cuenta</label>
            <select class="form-select" (change)="patchContacto.emit({ tipo_de_cuenta: $any($event.target).value })">
              <option value="" [selected]="c.tipo_de_cuenta === ''">Seleccione...</option>
              <option value="Cuenta de ahorros" [selected]="c.tipo_de_cuenta === 'Cuenta de ahorros'">Cuenta de ahorros</option>
              <option value="Cuenta corriente" [selected]="c.tipo_de_cuenta === 'Cuenta corriente'">Cuenta corriente</option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold">Número de cuenta</label>
            <input class="form-control" [value]="c.numero_de_cuenta"
              (input)="patchContacto.emit({ numero_de_cuenta: leer($event, soloDigitos) })" placeholder="Número de cuenta"
              inputmode="numeric" maxlength="30" />
          </div>

          <div class="mb-0">
            <label class="form-label fw-semibold">Verifica número de cuenta</label>
            <input class="form-control" [value]="c.numero_de_cuenta_verifica"
              (input)="patchContacto.emit({ numero_de_cuenta_verifica: leer($event, soloDigitos) })"
              placeholder="Repite el número de cuenta" inputmode="numeric" maxlength="30" />
            @if (c.numero_de_cuenta_verifica !== '' && c.numero_de_cuenta !== c.numero_de_cuenta_verifica) {
              <div class="form-text text-danger">
                <i class="bi bi-exclamation-circle me-1"></i>Los números de cuenta no coinciden
              </div>
            }
          </div>
        </div>
      </div>

      <!-- ── Bloque Certificados (beneficios tributarios) ── -->
      <div class="col-12">
        <div class="border rounded p-3">
          <p class="mb-3" style="font-weight: 500">
            5. Para efectos de obtener los beneficios tributarios me permito adjuntar los siguientes certificados:
          </p>
          <div class="row g-3">
            @for (cert of certificados; track cert.tipo) {
              <div class="col-12 col-md-6">
                <app-certificado-row [label]="cert.label" [tipo]="cert.tipo" [tipoPrefix]="cert.prefijo"
                  [numeroDocumento]="c.numero_documento" [existingDoc]="doc(cert.tipo)" [uploader]="uploader()"
                  (uploaded)="docsCambiaron.emit()" (deleted)="docsCambiaron.emit()"
                  (uploadingChange)="uploadingChange.emit($event)" />
              </div>
            }
          </div>
        </div>
      </div>

      <!-- ── Bloque Documentos de usuario ── -->
      <div class="col-12">
        <div class="border rounded p-3">
          <p class="mb-3" style="font-weight: 500">Documentos de usuario:</p>
          <div class="row g-3">
            @for (cert of documentosUsuario; track cert.tipo) {
              <div class="col-12 col-md-6">
                <app-certificado-row [label]="cert.label" [tipo]="cert.tipo" [tipoPrefix]="cert.prefijo"
                  [numeroDocumento]="c.numero_documento" [existingDoc]="doc(cert.tipo)" [uploader]="uploader()"
                  (uploaded)="docsCambiaron.emit()" (deleted)="docsCambiaron.emit()"
                  (uploadingChange)="uploadingChange.emit($event)" />
              </div>
            }
          </div>
        </div>
      </div>
    </div>
  `,
})
export class TributarioCamposComponent {
  readonly tributario = input.required<FormTributario>();
  readonly contacto = input.required<DatosComision>();
  readonly docs = input<DocTributario[] | undefined>(undefined);
  readonly uploader = input.required<DocumentoUploader>();
  readonly eps = input<OpcionBuscador[]>([]);
  readonly afp = input<OpcionBuscador[]>([]);
  readonly arl = input<OpcionBuscador[]>([]);
  readonly bancos = input<OpcionBuscador[]>([]);
  /** Prefijo de ids de los radios (p. ej. 'perfil-mov-'). */
  readonly prefijoId = input<string>('');
  /** Sufijo del atributo name de los radios (p. ej. '-perfil-mov'). */
  readonly sufijoName = input<string>('');
  readonly preguntaComision = input<string>('¿El asesor trabaja con o sin comisión?');
  /** Perfil propio: buscadores sin reapertura al vaciar ni "Sin resultados". */
  readonly modoSimple = input<boolean>(false);

  readonly tributarioChange = output<Partial<FormTributario>>();
  readonly patchContacto = output<Partial<DatosComision>>();
  readonly docsCambiaron = output<void>();
  readonly uploadingChange = output<boolean>();

  protected readonly certificados = CERTIFICADOS;
  protected readonly documentosUsuario = DOCUMENTOS_USUARIO;
  protected readonly noComisionEps = NO_COMISION_EPS;
  protected readonly noComisionAfp = NO_COMISION_AFP;
  protected readonly noComisionArl = NO_COMISION_ARL;
  protected readonly leer = leerInput;
  protected readonly soloDigitos = soloDigitos;

  protected readonly epsOpts = computed(() => this.eps());
  protected readonly afpOpts = computed(() => this.afp());
  protected readonly arlOpts = computed(() => this.arl());
  protected readonly bancoOpts = computed(() => this.bancos());

  protected doc(tipo: number): DocTributario | null {
    return docPorTipo(this.docs(), tipo);
  }

  protected patchT(cambios: Partial<FormTributario>): void {
    this.tributarioChange.emit(cambios);
  }
}
