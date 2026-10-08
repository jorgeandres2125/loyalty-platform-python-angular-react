import { useMemo } from 'react';
import { Row, Col } from 'react-bootstrap';
import { IconPillButton } from './IconPillButton';

interface Option {
  value: string;
  label: string;
  icon: string;
}

const OPTIONS: readonly Option[] = [
  { value: 'leer', label: 'a. Leer', icon: 'bi-book-fill' },
  { value: 'escuchar musica', label: 'b. Escuchar música', icon: 'bi-music-note-beamed' },
  { value: 'escribir', label: 'c. Escribir', icon: 'bi-pencil-fill' },
  { value: 'hacer deporte', label: 'd. Hacer deporte', icon: 'bi-bicycle' },
  { value: 'navegar en internet', label: 'e. Navegar en internet', icon: 'bi-laptop-fill' },
  { value: 'cocinar', label: 'f. Cocinar', icon: 'bi-egg-fried' },
  { value: 'ver television', label: 'g. Ver televisión', icon: 'bi-tv-fill' },
  { value: 'ir al cine', label: 'h. Ir al cine', icon: 'bi-film' },
  { value: 'salir con amigos', label: 'i. Salir con amigos', icon: 'bi-people-fill' },
  { value: 'estar con la familia', label: 'j. Estar con la familia', icon: 'bi-house-heart-fill' },
] as const;

function normalize(s: string): string {
  return s.toLowerCase().normalize('NFC').trim();
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

export function HobbiesSelector({ value, onChange }: Props) {
  const selected: string[] = useMemo(() => parseSelection(value), [value]);

  function toggle(optValue: string): void {
    const norm: string = normalize(optValue);
    const next: string[] = selected.includes(norm)
      ? selected.filter(v => v !== norm)
      : [...selected, norm];
    onChange(next.length === 0 ? '' : JSON.stringify(next));
  }

  return (
    <Row className="g-2">
      {OPTIONS.map(opt => {
        const isChecked: boolean = selected.includes(normalize(opt.value));
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
