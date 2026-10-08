import { useMemo } from 'react';
import { Row, Col } from 'react-bootstrap';
import { IconPillButton } from './IconPillButton';

interface Option {
  value: string;
  label: string;
  icon: string;
}

const OPTIONS: readonly Option[] = [
  { value: 'solo', label: 'A. Solo', icon: 'bi-person-fill' },
  { value: 'con mi pareja', label: 'B. Con mi pareja', icon: 'bi-suit-heart-fill' },
  { value: 'con mis hijos', label: 'C. Con mis hijos', icon: 'bi-people-fill' },
  { value: 'con mis papás', label: 'D. Con mis papás', icon: 'bi-house-heart-fill' },
  { value: 'con mis amigos', label: 'E. Con mis amigos', icon: 'bi-emoji-smile-fill' },
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

export function ConQuienVivesSelector({ value, onChange }: Props) {
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
          <Col xs={12} md key={opt.value}>
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
