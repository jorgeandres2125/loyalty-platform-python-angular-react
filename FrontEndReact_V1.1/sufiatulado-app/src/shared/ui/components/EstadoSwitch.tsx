import { Form } from 'react-bootstrap';

interface EstadoSwitchProps {
  id: string;
  checked: boolean;
  onChange: (value: boolean) => void;
  labelActivo?: string;
  labelInactivo?: string;
  compact?: boolean;
  disabled?: boolean;
  className?: string;
}

export function EstadoSwitch({
  id,
  checked,
  onChange,
  labelActivo = 'Activo',
  labelInactivo = 'Inactivo',
  compact = false,
  disabled = false,
  className = '',
}: EstadoSwitchProps) {
  if (compact) {
    return (
      <Form.Check
        type="switch"
        id={id}
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className={`mb-0 ${className}`}
        title={checked ? labelActivo : labelInactivo}
        style={{ transform: 'scale(1.3)', transformOrigin: 'center center' }}
      />
    );
  }
  return (
    <div
      className={`d-inline-flex align-items-center gap-3 px-4 py-3 rounded-3 border ${className}`}
      style={{
        background: checked
          ? 'rgba(25, 135, 84, 0.07)'
          : 'rgba(108, 117, 125, 0.07)',
        borderColor: checked
          ? 'rgba(25, 135, 84, 0.25) !important'
          : 'rgba(108, 117, 125, 0.2) !important',
        transition: 'background 0.2s ease',
        cursor: disabled ? 'not-allowed' : 'pointer',
        minWidth: 190,
      }}
      onClick={() => !disabled && onChange(!checked)}
      role="group"
      aria-label="Estado"
    >
      <Form.Check
        type="switch"
        id={id}
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        onClick={(e) => e.stopPropagation()}
        className="mb-0"
        style={{ flexShrink: 0, transform: 'scale(1.35)', transformOrigin: 'left center' }}
      />
      <div className="d-flex flex-column" style={{ lineHeight: 1.3 }}>
        <small className="text-muted" style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
          Estado
        </small>
        <span
          className="fw-semibold"
          style={{
            fontSize: '1rem',
            color: checked ? '#198754' : '#6c757d',
            transition: 'color 0.2s ease',
          }}
        >
          {checked ? (
            <><i className="bi bi-check-circle-fill me-1" style={{ fontSize: '0.85rem' }} />{labelActivo}</>
          ) : (
            <><i className="bi bi-dash-circle me-1" style={{ fontSize: '0.85rem' }} />{labelInactivo}</>
          )}
        </span>
      </div>
    </div>
  );
}
