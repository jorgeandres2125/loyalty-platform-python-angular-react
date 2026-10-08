import { useMemo } from 'react';
import { Row, Col } from 'react-bootstrap';
import { IconPillButton } from './IconPillButton';

interface Option {
  value: string;
  label: string;
  icon: string;
}

const FIXED_OPTIONS: readonly Option[] = [
  { value: 'Crecer Conocimiento en ventas',      label: 'a. Crecer conocimiento en ventas',      icon: 'bi-graph-up-arrow'     },
  { value: 'Aprender sobre marketing digital',   label: 'b. Marketing digital',                  icon: 'bi-megaphone-fill'     },
  { value: 'Saber sobre servicio al cliente',    label: 'c. Servicio al cliente',                icon: 'bi-headset'            },
  { value: 'Entender al consumidor',             label: 'd. Entender al consumidor',             icon: 'bi-person-check-fill'  },
  { value: 'Mejorar habilidades de negociacion', label: 'e. Habilidades de negociación',         icon: 'bi-award-fill'         },
  { value: 'Aprender otro idioma',               label: 'f. Aprender otro idioma',               icon: 'bi-translate'          },
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

export function PropositosCompetenciasSelector({ value, onChange }: Props) {
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
              color="purple"
              selected={isChecked}
              onClick={() => toggle(opt.value)}
            />
          </Col>
        );
      })}
    </Row>
  );
}
