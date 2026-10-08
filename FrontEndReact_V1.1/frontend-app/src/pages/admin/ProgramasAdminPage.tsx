import { useEffect, useState } from 'react';
import { Alert, Button, Card, Form, Spinner, Table } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import {
  useActualizarAdminPrograma,
  useAdminProgramasList,
} from '../../features/admin-programas/model/useAdminProgramas';
import type { AdminProgramaItem } from '../../features/admin-programas/model/types';

export function ProgramasAdminPage() {
  const navigate = useNavigate();
  const lista = useAdminProgramasList();
  const actualizarMut = useActualizarAdminPrograma();

  const [editId, setEditId] = useState<number | null>(null);
  const [nombre, setNombre] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  useEffect(() => {
    if (!success) return;
    const t = setTimeout(() => setSuccess(''), 3500);
    return () => clearTimeout(t);
  }, [success]);

  const handleEditar = (item: AdminProgramaItem) => {
    setEditId(item.cpid);
    setNombre(item.cp_nombre);
    setError('');
  };

  const handleCancelar = () => {
    setEditId(null);
    setNombre('');
    setError('');
  };

  const handleGuardar = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (editId === null) return;
    if (!nombre.trim()) { setError('El nombre del programa es obligatorio'); return; }
    try {
      await actualizarMut.mutateAsync({ cpid: editId, payload: { cp_nombre: nombre.trim() } });
      setSuccess('Programa actualizado correctamente');
      setEditId(null);
      setNombre('');
    } catch (err) {
      setError(extractError(err, 'Error al actualizar el programa'));
    }
  };

  return (
    <div>
      <PageHeader
        title="Administrar Programas"
        subtitle="Solo edición del nombre — los códigos cpid están cableados al dominio (1=Movilidad, 2=Consumo)."
        icon="bi-bookmark-star-fill"
      />
      <div className="mb-3">
        <Button size="sm" variant="outline-secondary" onClick={() => navigate('/admin/catalogos')}>
          <i className="bi bi-arrow-left me-1" />Volver
        </Button>
      </div>

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')}>
          <i className="bi bi-check-circle me-2" />{success}
        </Alert>
      )}

      <Card className="border-0 shadow-sm">
        <Card.Body className="p-0">
          {lista.isLoading ? (
            <div className="text-center py-5"><Spinner animation="border" /></div>
          ) : lista.isError ? (
            <Alert variant="danger" className="m-3">Error al cargar los programas</Alert>
          ) : (
            <Table hover responsive className="mb-0 align-middle">
              <thead className="table-light">
                <tr>
                  <th style={{ width: 100 }}>cpid</th>
                  <th>Nombre</th>
                  <th className="text-end" style={{ width: 180 }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {(lista.data ?? []).map((p) => (
                  <tr key={p.cpid}>
                    <td><code>{p.cpid}</code></td>
                    <td>
                      {editId === p.cpid ? (
                        <Form onSubmit={handleGuardar} className="d-flex gap-2 align-items-center">
                          <Form.Control
                            type="text"
                            size="sm"
                            maxLength={50}
                            value={nombre}
                            onChange={(e) => setNombre(e.target.value)}
                            autoFocus
                            style={{ maxWidth: 300 }}
                          />
                          <Button type="submit" size="sm" variant="primary" disabled={actualizarMut.isPending}>
                            {actualizarMut.isPending
                              ? <Spinner size="sm" animation="border" />
                              : <i className="bi bi-check-lg" />}
                          </Button>
                          <Button type="button" size="sm" variant="outline-secondary" onClick={handleCancelar} disabled={actualizarMut.isPending}>
                            <i className="bi bi-x-lg" />
                          </Button>
                        </Form>
                      ) : (
                        <span className="fw-semibold">{p.cp_nombre}</span>
                      )}
                    </td>
                    <td className="text-end">
                      {editId !== p.cpid && (
                        <Button size="sm" variant="outline-primary" onClick={() => handleEditar(p)}>
                          <i className="bi bi-pencil-fill me-1" />Editar nombre
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {editId !== null && error && (
        <Alert variant="danger" className="mt-3">
          <i className="bi bi-exclamation-triangle me-2" />{error}
        </Alert>
      )}
    </div>
  );
}

function extractError(err: unknown, fallback: string): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
  if (Array.isArray(detail)) return detail.join('; ');
  if (typeof detail === 'string') return detail;
  if (err instanceof Error) return err.message;
  return fallback;
}
