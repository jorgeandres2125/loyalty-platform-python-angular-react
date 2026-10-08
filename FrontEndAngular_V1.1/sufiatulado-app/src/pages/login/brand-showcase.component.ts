import { ChangeDetectionStrategy, Component, computed, effect, signal } from '@angular/core';
import { BrandLogoComponent } from '../../shared/ui/components/brand-logo.component';

interface Slide {
  tag: string;
  icon: string;
  title: string;
  body: string;
  accent: string;
  image: string;
}

const SLIDES: readonly Slide[] = [
  {
    tag: 'Sufi Contigo',
    icon: 'bi-stars',
    title: 'Para pensar en grande, para lograr en grande.',
    body: 'Es un programa que te acompaña a alcanzar tus propósitos, impulsarte a que logres todo lo que te propones, apoyarte en todo momento y darte una mano siempre que la necesites.',
    accent: '#FF0026',
    image: 'assets/showcase/showcase-1-contigo.jpg',
  },
  {
    tag: 'Más experiencias',
    icon: 'bi-mortarboard-fill',
    title: 'Para sentirse privilegiado siempre.',
    body: 'Aprender cada día para servir con conocimiento. Retarse en cada proyecto para tener mejores resultados. Saber que eres el mejor para estar más motivado. Recibir recompensas cuando lo haces cada vez mejor.',
    accent: '#00D6C3',
    image: 'assets/showcase/showcase-2-experiencias.jpg',
  },
  {
    tag: 'Incentivos',
    icon: 'bi-gift-fill',
    title: 'Para ponerle más pasión a lo que haces.',
    body: 'En Sufi Contigo buscamos conocerte y es por eso que tenemos un plan de premios pensado especialmente en tus necesidades y propósitos; en el que recompensamos todo tu esfuerzo de una forma única y sorprendente.',
    accent: '#FFC100',
    image: 'assets/showcase/showcase-3-incentivos.jpg',
  },
];

const INTERVAL_MS = 7000;

@Component({
  selector: 'app-brand-showcase',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [BrandLogoComponent],
  host: { style: 'display: contents' },
  template: `
    <div class="brand-showcase" [style.--accent]="slide().accent">
      <!-- Background images per stage (crossfade + ken-burns) -->
      <div class="brand-showcase__media" aria-hidden="true">
        @for (s of slides; track s.tag; let i = $index) {
          <div
            class="brand-showcase__photo"
            [class.is-active]="i === active()"
            [style.background-image]="'url(' + s.image + ')'"
          ></div>
        }
      </div>

      <!-- Animated overlay -->
      <div class="brand-showcase__bg" aria-hidden="true">
        <span class="brand-showcase__orb brand-showcase__orb--1"></span>
        <span class="brand-showcase__orb brand-showcase__orb--2"></span>
        <span class="brand-showcase__orb brand-showcase__orb--3"></span>
        <span class="brand-showcase__grid"></span>
        <span class="brand-showcase__scrim"></span>
      </div>

      <!-- Header / logo -->
      <header class="brand-showcase__header">
        <app-brand-logo [height]="40" />
      </header>

      <!-- Rotating content (el @for con track por índice reinicia la animación de entrada) -->
      <div class="brand-showcase__stage">
        @for (k of [active()]; track k) {
          <div class="brand-showcase__slide">
            <div class="brand-showcase__icon">
              <i class="bi" [class]="slide().icon" aria-hidden="true"></i>
            </div>
            <span class="brand-showcase__tag">{{ slide().tag }}</span>
            <h2 class="brand-showcase__title">{{ slide().title }}</h2>
            <p class="brand-showcase__body">{{ slide().body }}</p>
          </div>
        }
      </div>

      <!-- Footer / progress dots -->
      <footer class="brand-showcase__footer">
        <div class="brand-showcase__dots" role="tablist" aria-label="Mensajes de Sufi Contigo">
          @for (s of slides; track s.tag; let i = $index) {
            <button
              type="button"
              role="tab"
              [attr.aria-selected]="i === active()"
              [attr.aria-label]="s.tag"
              class="brand-showcase__dot"
              [class.is-active]="i === active()"
              (click)="go(i)"
            >
              <span
                class="brand-showcase__dot-fill"
                [style.animation-duration]="i === active() ? intervalMs + 'ms' : null"
              ></span>
            </button>
          }
        </div>
        <p class="brand-showcase__tagline">Siempre a tu lado</p>
      </footer>
    </div>
  `,
})
export class BrandShowcaseComponent {
  protected readonly slides = SLIDES;
  protected readonly intervalMs = INTERVAL_MS;
  protected readonly active = signal<number>(0);
  protected readonly slide = computed<Slide>(() => SLIDES[this.active()]);

  constructor() {
    // El intervalo se reinicia cada vez que cambia la diapositiva activa.
    effect((onCleanup) => {
      this.active();
      const id = window.setInterval(() => {
        this.active.update((prev) => (prev + 1) % SLIDES.length);
      }, INTERVAL_MS);
      onCleanup(() => window.clearInterval(id));
    });
  }

  protected go(index: number): void {
    this.active.set(((index % SLIDES.length) + SLIDES.length) % SLIDES.length);
  }
}
