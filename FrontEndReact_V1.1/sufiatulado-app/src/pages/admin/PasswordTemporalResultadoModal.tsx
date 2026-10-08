import { Button, Modal } from 'react-bootstrap';
import type { PasswordTemporalResultado } from '../../features/admin-usuarios/model/types';

interface Props {
  resultado: PasswordTemporalResultado | null;
  onCerrar: () => void;
}

// AP-0047: muestra la clave temporal generada una unica vez (solo viaja en la
// respuesta de emision; el sistema persiste unicamente su hash).
export function PasswordTemporalResultadoModal({ resultado, onCerrar }: Props) {
  return (
    <Modal show={resultado !== null} onHide={onCerrar} centered>
      <Modal.Header closeButton>
        <Modal.Title as="h6">
          <i className="bi bi-key me-2" />
          Contrasena temporal generada
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p className="small text-muted mb-3">
          Entregala a <strong>{resultado?.usuario}</strong> por un canal seguro. Se
          muestra una sola vez, vence en{' '}
          {resultado?.ttl_minutos} minutos y el usuario debera definir su contrasena
          personal al ingresar.
        </p>
        <div className="p-3 bg-light border rounded text-center">
          <code className="fs-5 user-select-all">{resultado?.password_temporal}</code>
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" size="sm" onClick={onCerrar}>
          Cerrar
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
