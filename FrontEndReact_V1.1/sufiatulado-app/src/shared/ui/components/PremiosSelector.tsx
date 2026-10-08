import { useMemo } from 'react';
import { Row, Col } from 'react-bootstrap';
import { IconPillButton } from './IconPillButton';

interface Option {
  value: string;
  label: string;
  icon: string;
}

const OPTIONS: readonly Option[] = [
  { value: 'Experiencias', label: 'a. Experiencias', icon: 'bi-stars' },
  { value: 'Deporte', label: 'b. Deporte', icon: 'bi-trophy-fill' },
  { value: 'Tecnología', label: 'c. Tecnología', icon: 'bi-laptop-fill' },
  { value: 'Hogar', label: 'd. Hogar', icon: 'bi-house-heart-fill' },
  { value: 'Viajes', label: 'e. Viajes', icon: 'bi-airplane-fill' },
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

export function PremiosSelector({ value, onChange }: Props) {
  const selected: string[] = useMemo(() => parseSelection(value), [value]);

  function toggle(optValue: string): void {
    const norm: string = normalize(optValue);
    const isSelected: boolean = selected.some(v => v.toLowerCase() === norm.toLowerCase());
    const next: string[] = isSelected
      ? selected.filter(v => v.toLowerCase() !== norm.toLowerCase())
      : [...selected, norm];
    onChange(next.length === 0 ? '' : JSON.stringify(next));
  }

  return (
    <Row className="g-2">
      {OPTIONS.map(opt => {
        const optNorm: string = normalize(opt.value).toLowerCase();
        const isChecked: boolean = selected.some(v => v.toLowerCase() === optNorm);
        return (
          <Col xs={12} sm={6} md key={opt.value}>
            <IconPillButton
              label={opt.label}
              icon={opt.icon}
              color="gold"
              selected={isChecked}
              onClick={() => toggle(opt.value)}
            />
          </Col>
        );
      })}
    </Row>
  );
}
