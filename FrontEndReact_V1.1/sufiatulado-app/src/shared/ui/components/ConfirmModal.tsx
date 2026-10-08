import { type ReactNode } from 'react';
import { Button, Modal, Spinner } from 'react-bootstrap';

export type ConfirmVariant = 'primary' | 'danger' | 'warning' | 'success' | 'info';

interface ConfirmModalProps {
  show: boolean;
  title: string;
  message: ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  confirmVariant?: ConfirmVariant;
  confirmIcon?: string;
  loadingLabel?: string;
  loading?: boolean;
  size?: 'sm' | 'lg' | 'xl';
  onConfirm: () => void | Promise<void>;
  onHide: () => void;
}

export function ConfirmModal({
  show,
  title,
  message,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  confirmVariant = 'danger',
  confirmIcon = 'bi-check-circle',
  loadingLabel = 'Procesando…',
  loading = false,
  size,
  onConfirm,
  onHide,
}: ConfirmModalProps) {
  const handleConfirm = async () => {
    if (loading) return;
    await onConfirm();
  };

  const handleHide = () => {
    if (loading) return;
    onHide();
  };

  return (
    <Modal
      show={show}
      onHide={handleHide}
      centered
      size={size}
      backdrop={loading ? 'static' : true}
      keyboard={!loading}
    >
      <Modal.Header closeButton={!loading}>
        <Modal.Title>{title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>{message}</Modal.Body>
      <Modal.Footer>
        <Button variant="outline-secondary" onClick={handleHide} disabled={loading}>
          <i className="bi bi-x-circle me-1" />
          {cancelLabel}
        </Button>
        <Button variant={confirmVariant} onClick={handleConfirm} disabled={loading}>
          {loading ? (
            <>
              <Spinner animation="border" size="sm" className="me-1" />
              {loadingLabel}
            </>
          ) : (
            <>
              <i className={`bi ${confirmIcon} me-1`} />
              {confirmLabel}
            </>
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
