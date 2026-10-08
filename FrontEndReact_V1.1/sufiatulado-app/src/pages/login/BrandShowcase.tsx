import { useEffect, useState, useCallback } from 'react';
import { BrandLogo } from '../../shared/ui/components/BrandLogo';
import imgContigo from '../../assets/showcase/showcase-1-contigo.jpg';
import imgExperiencias from '../../assets/showcase/showcase-2-experiencias.jpg';
import imgIncentivos from '../../assets/showcase/showcase-3-incentivos.jpg';

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
    image: imgContigo,
  },
  {
    tag: 'Más experiencias',
    icon: 'bi-mortarboard-fill',
    title: 'Para sentirse privilegiado siempre.',
    body: 'Aprender cada día para servir con conocimiento. Retarse en cada proyecto para tener mejores resultados. Saber que eres el mejor para estar más motivado. Recibir recompensas cuando lo haces cada vez mejor.',
    accent: '#00D6C3',
    image: imgExperiencias,
  },
  {
    tag: 'Incentivos',
    icon: 'bi-gift-fill',
    title: 'Para ponerle más pasión a lo que haces.',
    body: 'En Sufi Contigo buscamos conocerte y es por eso que tenemos un plan de premios pensado especialmente en tus necesidades y propósitos; en el que recompensamos todo tu esfuerzo de una forma única y sorprendente.',
    accent: '#FFC100',
    image: imgIncentivos,
  },
];

const INTERVAL_MS = 7000;

export function BrandShowcase() {
  const [active, setActive] = useState(0);

  const go = useCallback((index: number) => {
    setActive(((index % SLIDES.length) + SLIDES.length) % SLIDES.length);
  }, []);

  useEffect(() => {
    const id = window.setInterval(() => {
      setActive((prev) => (prev + 1) % SLIDES.length);
    }, INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [active]);

  const slide = SLIDES[active];

  return (
    <div className="brand-showcase" style={{ ['--accent' as string]: slide.accent }}>
      {/* Background images per stage (crossfade + ken-burns) */}
      <div className="brand-showcase__media" aria-hidden="true">
        {SLIDES.map((s, i) => (
          <div
            key={s.tag}
            className={`brand-showcase__photo${i === active ? ' is-active' : ''}`}
            style={{ backgroundImage: `url(${s.image})` }}
          />
        ))}
      </div>

      {/* Animated overlay */}
      <div className="brand-showcase__bg" aria-hidden="true">
        <span className="brand-showcase__orb brand-showcase__orb--1" />
        <span className="brand-showcase__orb brand-showcase__orb--2" />
        <span className="brand-showcase__orb brand-showcase__orb--3" />
        <span className="brand-showcase__grid" />
        <span className="brand-showcase__scrim" />
      </div>

      {/* Header / logo */}
      <header className="brand-showcase__header">
        <BrandLogo height={40} />
      </header>

      {/* Rotating content */}
      <div className="brand-showcase__stage">
        <div className="brand-showcase__slide" key={active}>
          <div className="brand-showcase__icon">
            <i className={`bi ${slide.icon}`} aria-hidden="true" />
          </div>
          <span className="brand-showcase__tag">{slide.tag}</span>
          <h2 className="brand-showcase__title">{slide.title}</h2>
          <p className="brand-showcase__body">{slide.body}</p>
        </div>
      </div>

      {/* Footer / progress dots */}
      <footer className="brand-showcase__footer">
        <div className="brand-showcase__dots" role="tablist" aria-label="Mensajes de Sufi Contigo">
          {SLIDES.map((s, i) => (
            <button
              key={s.tag}
              type="button"
              role="tab"
              aria-selected={i === active}
              aria-label={s.tag}
              className={`brand-showcase__dot${i === active ? ' is-active' : ''}`}
              onClick={() => go(i)}
            >
              <span
                className="brand-showcase__dot-fill"
                style={{ animationDuration: i === active ? `${INTERVAL_MS}ms` : undefined }}
              />
            </button>
          ))}
        </div>
        <p className="brand-showcase__tagline">Siempre a tu lado</p>
      </footer>
    </div>
  );
}
