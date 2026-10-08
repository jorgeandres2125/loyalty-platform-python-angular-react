import { useMemo, useState } from 'react';
import { Button, Col, Form, Row } from 'react-bootstrap';
import '../../../styles/components/TieneHijosSelector.scss';
import { ConfirmModal } from './ConfirmModal';

interface Mascota {
  nombre: string;
}

interface Props {
  numeroMascotas: string;
  infoMascotas: string;
  onChange: (numeroMascotas: string, infoMascotas: string) => void;
}

const EMPTY_MASCOTA: Mascota = { nombre: '' };

function parseMascotas(raw: string): Mascota[] {
  if (!raw) return [];
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return (parsed as unknown[]).map((item: unknown): Mascota => {
      const obj = (item ?? {}) as Record<string, unknown>;
      return { nombre: String(obj.nombre ?? '') };
    });
  } catch {
    return [];
  }
}

function tieneMascotaFromState(numeroMascotas: string): boolean {
  const trimmed: string = (numeroMascotas ?? '').trim();
  if (!trimmed) return false;
  return trimmed.toLowerCase() !== 'no';
}

export function TieneMascotaSelector({ numeroMascotas, infoMascotas, onChange }: Props) {
  const tieneMascota: boolean = tieneMascotaFromState(numeroMascotas);
  const mascotas: Mascota[] = useMemo(() => parseMascotas(infoMascotas), [infoMascotas]);
  const [idxAEliminar, setIdxAEliminar] = useState<number | null>(null);

  const mascotaAEliminar: Mascota | null =
    idxAEliminar !== null && idxAEliminar < mascotas.length ? mascotas[idxAEliminar] : null;

  function emit(next: Mascota[]): void {
    if (next.length === 0) {
      onChange('No', '');
    } else {
      onChange('Si', JSON.stringify(next));
    }
  }

  function setRespuesta(value: 'no' | 'si'): void {
    if (value === 'no') {
      onChange('No', '');
    } else if (mascotas.length === 0) {
      emit([{ ...EMPTY_MASCOTA }]);
    } else {
      onChange('Si', JSON.stringify(mascotas));
    }
  }

  function updateMascota(index: number, nombre: string): void {
    emit(mascotas.map((mascota, i) => (i === index ? { nombre } : mascota)));
  }

  function addMascota(): void {
    emit([...mascotas, { ...EMPTY_MASCOTA }]);
  }

  function removeMascota(index: number): void {
    emit(mascotas.filter((_, i) => i !== index));
  }

  function confirmarEliminarMascota(): void {
    if (idxAEliminar === null) return;
    removeMascota(idxAEliminar);
    setIdxAEliminar(null);
  }

  return (
    <div>
      <div className="d-flex flex-wrap align-items-center gap-4">
        <Form.Check
          inline
          type="radio"
          id="tiene-mascota-no"
          name="tiene-mascota"
          label="No"
          checked={!tieneMascota}
          onChange={() => setRespuesta('no')}
        />
        <Form.Check
          inline
          type="radio"
          id="tiene-mascota-si"
          name="tiene-mascota"
          label={`Sí${tieneMascota ? ` (${mascotas.length})` : ''}`}
          checked={tieneMascota}
          onChange={() => setRespuesta('si')}
        />
      </div>

      {tieneMascota && (
        <div className="mt-3">
          {mascotas.map((mascota, idx) => (
            <div key={idx} className="hijos-row">
              <span className="hijo-index">Mascota {idx + 1}</span>
              <Row className="g-2 align-items-end">
                <Col xs={12} md>
                  <Form.Label className="small mb-1">
                    <i className="bi bi-patch-heart me-1 text-danger" />Nombre
                  </Form.Label>
                  <Form.Control
                    value={mascota.nombre}
                    onChange={e => updateMascota(idx, e.target.value)}
                    placeholder="Nombre de la mascota"
                    maxLength={100}
                  />
                </Col>
                <Col xs={12} md="auto">
                  <Button
                    variant="outline-danger"
                    size="sm"
                    className="w-100 hijo-remove"
                    onClick={() => setIdxAEliminar(idx)}
                  >
                    <i className="bi bi-trash me-1" />Eliminar
                  </Button>
                </Col>
              </Row>
            </div>
          ))}
          <Button variant="outline-danger" size="sm" className="mt-3" onClick={addMascota}>
            <i className="bi bi-plus-circle me-1" />Agregar mascota
          </Button>
        </div>
      )}

      <ConfirmModal
        show={idxAEliminar !== null}
        title="Eliminar mascota"
        message={
          mascotaAEliminar ? (
            <>
              ¿Seguro que quieres eliminar a{' '}
              <strong>{mascotaAEliminar.nombre || `Mascota ${(idxAEliminar ?? 0) + 1}`}</strong>?
              <br />
              <span className="text-muted small">Esta acción no se puede deshacer.</span>
            </>
          ) : null
        }
        confirmLabel="Sí, eliminar"
        confirmIcon="bi-trash"
        onConfirm={confirmarEliminarMascota}
        onHide={() => setIdxAEliminar(null)}
      />
    </div>
  );
}
