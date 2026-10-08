import { useMemo, useState } from 'react';
import { Button, Col, Form, Row } from 'react-bootstrap';
import '../../../styles/components/TieneHijosSelector.scss';
import { ConfirmModal } from './ConfirmModal';

export interface Hijo {
  nombre: string;
  genero: 'M' | 'F' | '';
  fecha_nacimiento: string;
}

interface Props {
  numeroHijos: string;
  infoHijos: string;
  onChange: (numeroHijos: string, infoHijos: string) => void;
}

const EMPTY_HIJO: Hijo = { nombre: '', genero: '', fecha_nacimiento: '' };

function parseHijos(raw: string): Hijo[] {
  if (!raw) return [];
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.map((item: unknown): Hijo => {
      const obj = (item ?? {}) as Record<string, unknown>;
      const generoRaw: string = String(obj.genero ?? '').toUpperCase();
      const genero: 'M' | 'F' | '' = generoRaw === 'M' || generoRaw === 'F' ? generoRaw : '';
      return {
        nombre: String(obj.nombre ?? ''),
        genero,
        fecha_nacimiento: String(obj.fecha_nacimiento ?? ''),
      };
    });
  } catch {
    return [];
  }
}

function tieneHijosFromState(numeroHijos: string): boolean {
  const trimmed: string = (numeroHijos ?? '').trim();
  if (!trimmed) return false;
  if (trimmed.toLowerCase() === 'no') return false;
  return true;
}

export function TieneHijosSelector({ numeroHijos, infoHijos, onChange }: Props) {
  const tieneHijos: boolean = tieneHijosFromState(numeroHijos);
  const hijos: Hijo[] = useMemo(() => parseHijos(infoHijos), [infoHijos]);
  const [idxAEliminar, setIdxAEliminar] = useState<number | null>(null);

  const hijoAEliminar: Hijo | null =
    idxAEliminar !== null && idxAEliminar < hijos.length ? hijos[idxAEliminar] : null;

  function emit(nextHijos: Hijo[]): void {
    if (nextHijos.length === 0) {
      onChange('No', '');
      return;
    }
    onChange(String(nextHijos.length), JSON.stringify(nextHijos));
  }

  function setRespuesta(value: 'no' | 'si'): void {
    if (value === 'no') {
      onChange('No', '');
    } else if (hijos.length === 0) {
      emit([{ ...EMPTY_HIJO }]);
    } else {
      // Already has children loaded, just sync count
      onChange(String(hijos.length), JSON.stringify(hijos));
    }
  }

  function updateHijo(index: number, field: keyof Hijo, value: string): void {
    const next: Hijo[] = hijos.map((h, i) => {
      if (i !== index) return h;
      if (field === 'genero') {
        const norm: string = value.toUpperCase();
        const genero: 'M' | 'F' | '' = norm === 'M' || norm === 'F' ? norm : '';
        return { ...h, genero };
      }
      return { ...h, [field]: value };
    });
    emit(next);
  }

  function addHijo(): void {
    emit([...hijos, { ...EMPTY_HIJO }]);
  }

  function removeHijo(index: number): void {
    const next: Hijo[] = hijos.filter((_, i) => i !== index);
    emit(next);
  }

  function confirmarEliminarHijo(): void {
    if (idxAEliminar === null) return;
    removeHijo(idxAEliminar);
    setIdxAEliminar(null);
  }

  return (
    <div>
      <div className="d-flex flex-wrap align-items-center gap-4">
        <Form.Check
          inline
          type="radio"
          id="tiene-hijos-no"
          name="tiene-hijos"
          label="No"
          checked={!tieneHijos}
          onChange={() => setRespuesta('no')}
        />
        <Form.Check
          inline
          type="radio"
          id="tiene-hijos-si"
          name="tiene-hijos"
          label={`Sí, ¿Cuántos?${tieneHijos ? ` (${hijos.length})` : ''}`}
          checked={tieneHijos}
          onChange={() => setRespuesta('si')}
        />
      </div>

      {tieneHijos && (
        <div className="mt-3">
          {hijos.map((h, idx) => (
            <div key={idx} className="hijos-row">
              <span className="hijo-index">Hijo {idx + 1}</span>
              <Row className="g-2 align-items-end">
                <Col xs={12} md={5}>
                  <Form.Label className="small mb-1">
                    <i className="bi bi-person me-1 text-danger" />Nombre
                  </Form.Label>
                  <Form.Control
                    value={h.nombre}
                    onChange={e => updateHijo(idx, 'nombre', e.target.value)}
                    placeholder="Nombre completo"
                    maxLength={120}
                  />
                </Col>
                <Col xs={6} md={2}>
                  <Form.Label className="small mb-1">
                    <i className="bi bi-gender-ambiguous me-1 text-danger" />Género
                  </Form.Label>
                  <Form.Select value={h.genero} onChange={e => updateHijo(idx, 'genero', e.target.value)}>
                    <option value="">Seleccione...</option>
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </Form.Select>
                </Col>
                <Col xs={6} md={3}>
                  <Form.Label className="small mb-1">
                    <i className="bi bi-calendar-date me-1 text-danger" />Fecha nacimiento
                  </Form.Label>
                  <Form.Control
                    type="date"
                    value={h.fecha_nacimiento}
                    onChange={e => updateHijo(idx, 'fecha_nacimiento', e.target.value)}
                  />
                </Col>
                <Col xs={12} md={2}>
                  <Button
                    variant="outline-danger"
                    size="sm"
                    className="w-100 hijo-remove"
                    onClick={() => setIdxAEliminar(idx)}
                    title="Eliminar hijo"
                  >
                    <i className="bi bi-trash me-1" />Eliminar
                  </Button>
                </Col>
              </Row>
            </div>
          ))}
          <Button variant="outline-danger" size="sm" className="mt-3" onClick={addHijo}>
            <i className="bi bi-plus-circle me-1" />Agregar hijo
          </Button>
        </div>
      )}

      <ConfirmModal
        show={idxAEliminar !== null}
        title="Eliminar hijo"
        message={
          hijoAEliminar ? (
            <>
              ¿Seguro que quieres eliminar a{' '}
              <strong>{hijoAEliminar.nombre || `Hijo ${(idxAEliminar ?? 0) + 1}`}</strong>?
              <br />
              <span className="text-muted small">Esta acción no se puede deshacer.</span>
            </>
          ) : null
        }
        confirmLabel="Sí, eliminar"
        confirmIcon="bi-trash"
        onConfirm={confirmarEliminarHijo}
        onHide={() => setIdxAEliminar(null)}
      />
    </div>
  );
}
