import { useMemo } from 'react';
import { Row, Col } from 'react-bootstrap';
import { IconPillButton } from './IconPillButton';

interface Option {
  value: string;
  label: string;
  icon: string;
}

const FIXED_OPTIONS: readonly Option[] = [
  { value: 'Hacer deporte',                    label: 'a. Hacer deporte',                    icon: 'bi-bicycle'           },
  { value: 'Atencion Medica Complementaria',   label: 'b. Atención Médica Complementaria',   icon: 'bi-heart-pulse-fill'  },
  { value: 'Belleza y Estetica',               label: 'c. Belleza y Estética',               icon: 'bi-stars'             },
  { value: 'Alimentacion Basica y Saludable',  label: 'd. Alimentación Saludable',           icon: 'bi-apple'             },
  { value: 'Yoga y Meditacion',                label: 'e. Yoga y Meditación',                icon: 'bi-peace-fill'        },
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

export function PropositosSaludSelector({ value, onChange }: Props) {
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
              color="teal"
              selected={isChecked}
              onClick={() => toggle(opt.value)}
            />
          </Col>
        );
      })}
    </Row>
  );
}
