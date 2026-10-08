import { useMemo } from 'react';
import { Row, Col } from 'react-bootstrap';
import { IconPillButton } from './IconPillButton';

interface Option {
  value: string;
  label: string;
  icon: string;
}

const FIXED_OPTIONS: readonly Option[] = [
  { value: 'a', label: 'a. Experiencias para pasar tiempo juntos', icon: 'bi-emoji-laughing-fill' },
  { value: 'b', label: 'b. Viajes y vacaciones', icon: 'bi-airplane-fill' },
  { value: 'c', label: 'c. Actividades lúdicas', icon: 'bi-controller' },
] as const;

const FIXED_KEYS: ReadonlySet<string> = new Set(FIXED_OPTIONS.map(o => o.value));

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

export function PropositosFamiliaresSelector({ value, onChange }: Props) {
  const selected: string[] = useMemo(
    () => parseSelection(value).filter(v => FIXED_KEYS.has(v)),
    [value],
  );

  function toggle(key: string): void {
    const isSelected: boolean = selected.includes(key);
    const next: string[] = isSelected
      ? selected.filter(v => v !== key)
      : [...selected, key];
    onChange(next.length === 0 ? '' : JSON.stringify(next));
  }

  return (
    <Row className="g-2">
      {FIXED_OPTIONS.map(opt => {
        const isChecked: boolean = selected.includes(opt.value);
        return (
          <Col xs={12} sm={6} md key={opt.value}>
            <IconPillButton
              label={opt.label}
              icon={opt.icon}
              color="red"
              selected={isChecked}
              onClick={() => toggle(opt.value)}
            />
          </Col>
        );
      })}
    </Row>
  );
}
