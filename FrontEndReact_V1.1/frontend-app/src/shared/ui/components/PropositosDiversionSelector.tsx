import { useMemo } from 'react';
import { Row, Col } from 'react-bootstrap';
import { IconPillButton } from './IconPillButton';

interface Option {
  value: string;
  label: string;
  icon: string;
}

const FIXED_OPTIONS: readonly Option[] = [
  { value: 'Cine',                                          label: 'a. Cine',                          icon: 'bi-film'          },
  { value: 'Cocina',                                        label: 'b. Cocina',                        icon: 'bi-egg-fried'     },
  { value: 'Maquillaje',                                    label: 'c. Maquillaje',                    icon: 'bi-stars'         },
  { value: 'Asados',                                        label: 'd. Asados',                        icon: 'bi-fire'          },
  { value: 'Lectura',                                       label: 'e. Lectura',                       icon: 'bi-book-fill'     },
  { value: 'Video Juegos',                                  label: 'f. Video Juegos',                  icon: 'bi-controller'    },
  { value: 'Entretenimiento en el Hogar/Suscripcion TV',    label: 'g. Entret. Hogar / Suscripción TV', icon: 'bi-tv-fill'      },
] as const;

function normalize(s: string): string {
  return s.normalize('NFC').trim();
}

function parseSelection(raw: string): string[] {
  if (!raw) return [];
  try {
    const parsed: unknown = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed.map(v => normalize(String(v)));
  } catch {
    return raw.split(',').map(s => normalize(s)).filter(Boolean);
  }
  return [];
}

interface Props {
  value: string;
  onChange: (next: string) => void;
}

export function PropositosDiversionSelector({ value, onChange }: Props) {
  const selected: string[] = useMemo(() => parseSelection(value), [value]);

  function toggle(optValue: string): void {
    const norm: string = optValue.toLowerCase();
    const isSelected: boolean = selected.some(v => v.toLowerCase() === norm);
    const next: string[] = isSelected
      ? selected.filter(v => v.toLowerCase() !== norm)
      : [...selected, optValue];
    onChange(next.length === 0 ? '' : JSON.stringify(next));
  }

  return (
    <Row className="g-2">
      {FIXED_OPTIONS.map(opt => {
        const optNorm: string = opt.value.toLowerCase();
        const isChecked: boolean = selected.some(v => v.toLowerCase() === optNorm);
        return (
          <Col xs={12} sm={6} md key={opt.value}>
            <IconPillButton
              label={opt.label}
              icon={opt.icon}
              color="orange"
              selected={isChecked}
              onClick={() => toggle(opt.value)}
            />
          </Col>
        );
      })}
    </Row>
  );
}
