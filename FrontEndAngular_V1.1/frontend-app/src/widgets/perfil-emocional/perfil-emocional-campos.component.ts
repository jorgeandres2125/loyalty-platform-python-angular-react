import { ChangeDetectionStrategy, Component, computed, input, model } from '@angular/core';
import { MetroTileToggleComponent } from '../../shared/ui/components/metro-tile-toggle.component';
import {
  TomSelectBuscadorComponent,
  type OpcionBuscador,
} from '../../shared/ui/components/tom-select-buscador.component';
import { TieneHijosSelectorComponent } from '../../shared/ui/components/tiene-hijos-selector.component';
import { TieneMascotaSelectorComponent } from '../../shared/ui/components/tiene-mascota-selector.component';
import { ConQuienVivesSelectorComponent } from '../../shared/ui/components/con-quien-vives-selector.component';
import { PremiosSelectorComponent } from '../../shared/ui/components/premios-selector.component';
import { HobbiesSelectorComponent } from '../../shared/ui/components/hobbies-selector.component';
import { TemasProfundizarSelectorComponent } from '../../shared/ui/components/temas-profundizar-selector.component';
import { PropositosFamiliaresSelectorComponent } from '../../shared/ui/components/propositos-familiares-selector.component';
import { PropositosFinancierosSelectorComponent } from '../../shared/ui/components/propositos-financieros-selector.component';
import { PropositosDiversionSelectorComponent } from '../../shared/ui/components/propositos-diversion-selector.component';
import { PropositosSaludSelectorComponent } from '../../shared/ui/components/propositos-salud-selector.component';
import { PropositosCompetenciasSelectorComponent } from '../../shared/ui/components/propositos-competencias-selector.component';
import { badgeCount, type FormEmocional } from './perfil-emocional';

const ESTADOS_CIVILES: readonly string[] = ['Soltero/a', 'Casado/a', 'Unión libre', 'Divorciado/a', 'Viudo/a'];
const NIVELES_EDUCATIVOS: readonly string[] = [
  'Bachiller',
  'Técnico',
  'Tecnológico',
  'Universitario',
  'Postgrado',
  'Doctorado',
];

/**
 * Campos del perfil emocional, idénticos en el registro de asesores (Consumo/Movilidad)
 * y en el perfil propio del comisionista. `persona` ajusta los textos: los asesores
 * hablan en tercera persona ("¿Con quién vive?") y el perfil propio en segunda
 * ("¿Con quién vives?"). Soporta `[(emocional)]`.
 */
@Component({
  selector: 'app-perfil-emocional-campos',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    MetroTileToggleComponent,
    TomSelectBuscadorComponent,
    TieneHijosSelectorComponent,
    TieneMascotaSelectorComponent,
    ConQuienVivesSelectorComponent,
    PremiosSelectorComponent,
    HobbiesSelectorComponent,
    TemasProfundizarSelectorComponent,
    PropositosFamiliaresSelectorComponent,
    PropositosFinancierosSelectorComponent,
    PropositosDiversionSelectorComponent,
    PropositosSaludSelectorComponent,
    PropositosCompetenciasSelectorComponent,
  ],
  template: `
    @let e = emocional();
    <div class="row g-3">
      <div class="col-md-4">
        <label class="form-label"><i class="bi bi-heart me-1 text-danger"></i>Estado Civil</label>
        <select class="form-select" (change)="set('estado_civil', $any($event.target).value)">
          <option value="" [selected]="e.estado_civil === ''">Seleccione...</option>
          @for (op of estadosCiviles; track op) {
            <option [value]="op" [selected]="op === e.estado_civil">{{ op }}</option>
          }
        </select>
      </div>
      <div class="col-12">
        <label class="form-label"><i class="bi bi-person-hearts me-1 text-danger"></i>¿Tiene hijos?</label>
        <app-tiene-hijos-selector
          [numeroHijos]="e.numero_hijos"
          [infoHijos]="e.info_hijos"
          (changed)="patch({ numero_hijos: $event.numeroHijos, info_hijos: $event.infoHijos })"
        />
      </div>
      <div class="col-12">
        <label class="form-label"><i class="bi bi-patch-heart me-1 text-danger"></i>¿Tiene mascota?</label>
        <app-tiene-mascota-selector
          [numeroMascotas]="e.numero_mascotas"
          [infoMascotas]="e.info_mascotas"
          (changed)="patch({ numero_mascotas: $event.numeroMascotas, info_mascotas: $event.infoMascotas })"
        />
      </div>
      <div class="col-md-4">
        <label class="form-label"><i class="bi bi-mortarboard me-1 text-danger"></i>Nivel Educativo</label>
        <select class="form-select" (change)="set('nivel_educativo', $any($event.target).value)">
          <option value="" [selected]="e.nivel_educativo === ''">Seleccione...</option>
          @for (op of nivelesEducativos; track op) {
            <option [value]="op" [selected]="op === e.nivel_educativo">{{ op }}</option>
          }
        </select>
      </div>
      <div class="col-md-4">
        <label class="form-label"><i class="bi bi-briefcase me-1 text-danger"></i>Profesión</label>
        @if (profesiones().length) {
          <app-tom-select-buscador
            [options]="profesiones()"
            [value]="e.profesion"
            (valueChange)="set('profesion', $event)"
            placeholder="Seleccione o busque una profesión..."
            [sinResultados]="!profesionSimple()"
            [reabrirAlLimpiar]="!profesionSimple()"
          />
        } @else {
          <select class="form-select"></select>
        }
      </div>
      <div class="col-12">
        <app-metro-tile-toggle [title]="t().conQuien" icon="bi-people-fill" color="red" size="medium"
          subtitle="Selecciona una o varias opciones" [badge]="badge(e.con_quien_vives)">
          <app-con-quien-vives-selector [value]="e.con_quien_vives" (valueChange)="set('con_quien_vives', $event)" />
        </app-metro-tile-toggle>
      </div>
      <div class="col-12">
        <app-metro-tile-toggle [title]="t().premios" icon="bi-trophy-fill" color="gold" size="medium"
          [subtitle]="t().premiosSub" [badge]="badge(e.premios_gustaria_recibir)">
          <app-premios-selector [value]="e.premios_gustaria_recibir" (valueChange)="set('premios_gustaria_recibir', $event)" />
        </app-metro-tile-toggle>
      </div>
      <div class="col-12">
        <app-metro-tile-toggle title="¿Cuáles son tus Hobbies?" icon="bi-controller" color="teal" size="wide"
          subtitle="Despliega para elegir hasta 10 hobbies" [badge]="badge(e.hobbies)">
          <div class="metro-hobbies-grid">
            <app-hobbies-selector [value]="e.hobbies" (valueChange)="set('hobbies', $event)" />
          </div>
        </app-metro-tile-toggle>
      </div>
      <div class="col-12">
        <app-metro-tile-toggle title="¿En qué temas te gustaría profundizar o aprender?" icon="bi-book-half" color="blue"
          size="medium" subtitle="Selecciona los temas de interés" [badge]="badge(e.temas_a_profundizar)">
          <app-temas-profundizar-selector [value]="e.temas_a_profundizar" (valueChange)="set('temas_a_profundizar', $event)" />
        </app-metro-tile-toggle>
      </div>
      <div class="col-12">
        <app-metro-tile-toggle title="Propósitos con tu Familia" icon="bi-house-heart-fill" color="red" size="medium"
          subtitle="Marca los propósitos familiares" [badge]="badge(e.propositos_familiares)">
          <app-propositos-familiares-selector [value]="e.propositos_familiares" (valueChange)="set('propositos_familiares', $event)" />
        </app-metro-tile-toggle>
      </div>
      <div class="col-12">
        <app-metro-tile-toggle title="Propósitos Financieros" icon="bi-currency-dollar" color="green" size="medium"
          subtitle="Selecciona los propósitos financieros" [badge]="badge(e.propositos_financieros)">
          <app-propositos-financieros-selector [value]="e.propositos_financieros" (valueChange)="set('propositos_financieros', $event)" />
        </app-metro-tile-toggle>
      </div>
      <div class="col-12">
        <app-metro-tile-toggle title="Propósitos Diversión" icon="bi-joystick" color="yellow" size="wide"
          subtitle="Despliega para elegir actividades de diversión" [badge]="badge(e.propositos_diversion)">
          <div class="metro-twocol-grid">
            <app-propositos-diversion-selector [value]="e.propositos_diversion" (valueChange)="set('propositos_diversion', $event)" />
          </div>
        </app-metro-tile-toggle>
      </div>
      <div class="col-12">
        <app-metro-tile-toggle title="Propósitos Salud" icon="bi-heart-pulse-fill" color="teal" size="medium"
          subtitle="Selecciona los propósitos de salud y bienestar" [badge]="badge(e.propositos_salud)">
          <app-propositos-salud-selector [value]="e.propositos_salud" (valueChange)="set('propositos_salud', $event)" />
        </app-metro-tile-toggle>
      </div>
      <div class="col-12">
        <app-metro-tile-toggle title="Propósitos Competencias" icon="bi-award-fill" color="navy" size="wide"
          subtitle="Despliega para elegir competencias a desarrollar" [badge]="badge(e.propositos_competencias)">
          <div class="metro-twocol-grid">
            <app-propositos-competencias-selector [value]="e.propositos_competencias" (valueChange)="set('propositos_competencias', $event)" />
          </div>
        </app-metro-tile-toggle>
      </div>
      <div class="col-12">
        <div class="form-check">
          <input class="form-check-input" type="checkbox" [id]="terminosId()" [checked]="e.acepto_terminos_y_condiciones"
            (change)="set('acepto_terminos_y_condiciones', $any($event.target).checked)" />
          <label class="form-check-label" [for]="terminosId()">Acepto los términos y condiciones *</label>
        </div>
      </div>
    </div>
  `,
})
export class PerfilEmocionalCamposComponent {
  readonly emocional = model.required<FormEmocional>();
  readonly profesiones = input<OpcionBuscador[]>([]);
  /** 'tercera' (asesor registra a un comisionista) o 'segunda' (perfil propio). */
  readonly persona = input<'tercera' | 'segunda'>('tercera');
  readonly terminosId = input<string>('terminos-emocional');
  /** Perfil propio: el buscador de profesión no reabre al vaciar ni muestra "Sin resultados". */
  readonly profesionSimple = input<boolean>(false);

  protected readonly estadosCiviles = ESTADOS_CIVILES;
  protected readonly nivelesEducativos = NIVELES_EDUCATIVOS;

  protected readonly t = computed(() =>
    this.persona() === 'segunda'
      ? {
          conQuien: '¿Con quién vives?',
          premios: 'Premios que te gustaría recibir',
          premiosSub: 'Marca todos los premios de tu interés',
        }
      : {
          conQuien: '¿Con quién vive?',
          premios: 'Premios que le gustaría recibir',
          premiosSub: 'Marca todos los premios de su interés',
        },
  );

  protected badge(valor: string): number | null {
    return badgeCount(valor);
  }

  protected set<K extends keyof FormEmocional>(campo: K, valor: FormEmocional[K]): void {
    this.emocional.update((prev) => ({ ...prev, [campo]: valor }));
  }

  protected patch(cambios: Partial<FormEmocional>): void {
    this.emocional.update((prev) => ({ ...prev, ...cambios }));
  }
}
