import { Button, Modal } from 'react-bootstrap';

export interface IdleWarningModalProps {
  show: boolean;
  segundosRestantes: number;
  onContinuar: () => void;
  onCerrar: () => void;
}

export function IdleWarningModal({
  show,
  segundosRestantes,
  onContinuar,
  onCerrar,
}: IdleWarningModalProps): JSX.Element {
  return (
    <Modal show={show} onHide={onCerrar} backdrop="static" centered>
      <Modal.Header>
        <Modal.Title>Tu sesion esta por expirar</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        Por seguridad (AP-0129), tu sesion se cerrara por inactividad en{' '}
        <strong>{segundosRestantes}</strong> segundos. Deseas continuar conectado?
      </Modal.Body>
      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onCerrar}>
          Cerrar sesion
        </Button>
        <Button variant="primary" onClick={onContinuar}>
          Continuar conectado
        </Button>
      </Modal.Footer>
    </Modal>
  );
}