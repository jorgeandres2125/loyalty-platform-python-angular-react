import { Fragment, useState } from 'react';
import { Alert, Badge, Button, Card, Collapse, Form, Spinner, Table } from 'react-bootstrap';
import type { DocumentoEditPayload, DocumentoItem } from '../../features/documentos/model/types';
import {
  useAsesoresConDocumentos,
  useDocumentosAsesor,
  useEditarDocumento,
} from '../../features/documentos/model/useDocumentos';

const PROGRAMA_MOVILIDAD_ID = 1 as const;
const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];
const ESTADOS_DOCUMENTO: ReadonlyArray<{ value: string; label: string; bg: string }> = [
  { value: 'pendiente', label: 'Pendiente', bg: 'warning' },
  { value: 'revision', label: 'Revisión', bg: 'info' },
  { value: 'aprobado', label: 'Aprobado', bg: 'success' },
];

function estadoBadgeBg(estado: string): string {
  return ESTADOS_DOCUMENTO.find((estadoOpt) => estadoOpt.value === estado.toLowerCase())?.bg ?? 'secondary';
}

function estadoLabel(estado: string): string {
  return ESTADOS_DOCUMENTO.find((estadoOpt) => estadoOpt.value === estado.toLowerCase())?.label ?? estado;
}

function formatFechaInput(value: string | null): string {
  if (!value) return '';
  const date: Date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function formatFechaDisplay(value: string | null): string {
  if (!value) return '—';
  const date: Date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

interface DocumentoEditState {
  did: number;
  nombre: string;
  estado: string;
  fecha: string;
}

function DocumentosAsesor({ numeroDocumento }: { numeroDocumento: string }) {
  const docs = useDocumentosAsesor(numeroDocumento, true);
  const editar = useEditarDocumento(numeroDocumento);
  const [editId, setEditId] = useState<number | null>(null);
  const [edit, setEdit] = useState<DocumentoEditState | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const abrirEdicion = (d: DocumentoItem) => {
    setEditId(d.did);
    setEdit({
      did: d.did,
      nombre: d.nombre,
      estado: (d.estado || 'pendiente').toLowerCase(),
      fecha: formatFechaInput(d.fecha),
    });
    setErrorMsg('');
  };

  const cancelarEdicion = () => {
    setEditId(null);
    setEdit(null);
    setErrorMsg('');
  };

  const guardarEdicion = async () => {
    if (!edit) return;
    setErrorMsg('');
    const payload: DocumentoEditPayload = {
      nombre: edit.nombre,
      estado: edit.estado,
      fecha: edit.fecha ? new Date(edit.fecha).toISOString() : null,
    };
    try {
      await editar.mutateAsync({ did: edit.did, payload });
      cancelarEdicion();
    } catch (err) {
      const msg: string = err instanceof Error ? err.message : 'Error al guardar';
      setErrorMsg(msg);
    }
  };

  if (docs.isLoading) {
    return (
      <div className="text-center py-3">
        <Spinner animation="border" variant="danger" size="sm" />
      </div>
    );
  }

  if (!docs.data || docs.data.length === 0) {
    return (
      <div className="text-center py-3 text-muted small">
        <i className="bi bi-inbox me-2" />
        Sin documentos cargados para este asesor
      </div>
    );
  }

  return (
    <div className="p-3" style={{ background: '#f8f9fa' }}>
      <Table size="sm" hover className="mb-0 bg-white">
        <thead className="table-light">
          <tr>
            <th>Id</th>
            <th>Tipo de documento</th>
            <th>Documento</th>
            <th>Estado</th>
            <th className="text-center">Versión</th>
            <th>Fecha Alta</th>
            <th className="text-center">Operación</th>
          </tr>
        </thead>
        <tbody>
          {docs.data.map((doc: DocumentoItem) => (
            <tr key={doc.did}>
              <td className="font-monospace">{doc.did}</td>
              <td>{doc.tipo_nombre}</td>
              <td className="font-monospace">{doc.nombre}</td>
              <td>
                <Badge bg={estadoBadgeBg(doc.estado)}>{estadoLabel(doc.estado)}</Badge>
              </td>
              <td className="text-center">{doc.version}</td>
              <td>{formatFechaDisplay(doc.fecha)}</td>
              <td className="text-center">
                <Button
                  variant={editId === doc.did ? 'secondary' : 'outline-primary'}
                  size="sm"
                  onClick={() => (editId === doc.did ? cancelarEdicion() : abrirEdicion(doc))}
                >
                  <i className={`bi ${editId === doc.did ? 'bi-x-lg' : 'bi-pencil'} me-1`} />
                  {editId === doc.did ? 'Cerrar' : 'Editar'}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      {edit && (
        <Collapse in={editId !== null}>
          <div className="mt-3">
            <Card className="border-primary">
              <Card.Body>
                <h6 className="fw-semibold mb-3">
                  <i className="bi bi-pencil-square me-2 text-primary" />
                  Editar documento #{edit.did}
                </h6>
                {errorMsg && (
                  <Alert variant="danger" onClose={() => setErrorMsg('')} dismissible className="py-2">
                    {errorMsg}
                  </Alert>
                )}
                <div className="row g-3">
                  <div className="col-md-4">
                    <Form.Label className="small fw-semibold mb-1">Id Documento</Form.Label>
                    <Form.Control value={edit.did} readOnly disabled className="font-monospace" />
                  </div>
                  <div className="col-md-4">
                    <Form.Label className="small fw-semibold mb-1">Número documento asesor</Form.Label>
                    <Form.Control value={numeroDocumento} readOnly disabled className="font-monospace" />
                  </div>
                  <div className="col-md-4">
                    <Form.Label className="small fw-semibold mb-1">Nombre archivo</Form.Label>
                    <Form.Control
                      value={edit.nombre}
                      onChange={(e) => setEdit({ ...edit, nombre: e.target.value })}
                    />
                  </div>
                  <div className="col-md-4">
                    <Form.Label className="small fw-semibold mb-1">Versión</Form.Label>
                    <Form.Control
                      value={docs.data.find((doc) => doc.did === edit.did)?.version ?? 1}
                      readOnly
                      disabled
                    />
                  </div>
                  <div className="col-md-4">
                    <Form.Label className="small fw-semibold mb-1">Estado</Form.Label>
                    <Form.Select
                      value={edit.estado}
                      onChange={(e) => setEdit({ ...edit, estado: e.target.value })}
                    >
                      {ESTADOS_DOCUMENTO.map((es) => (
                        <option key={es.value} value={es.value}>{es.label}</option>
                      ))}
                    </Form.Select>
                  </div>
                  <div className="col-md-4">
                    <Form.Label className="small fw-semibold mb-1">Fecha de alta</Form.Label>
                    <Form.Control
                      type="datetime-local"
                      value={edit.fecha}
                      onChange={(e) => setEdit({ ...edit, fecha: e.target.value })}
                    />
                  </div>
                </div>
                <div className="d-flex justify-content-end gap-2 mt-3">
                  <Button variant="outline-secondary" onClick={cancelarEdicion} disabled={editar.isPending}>
                    <i className="bi bi-x-circle me-1" />Cancelar
                  </Button>
                  <Button variant="danger" onClick={guardarEdicion} disabled={editar.isPending}>
                    {editar.isPending ? (
                      <><Spinner animation="border" size="sm" className="me-1" />Guardando…</>
                    ) : (
                      <><i className="bi bi-check-circle me-1" />Guardar</>
                    )}
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </div>
        </Collapse>
      )}
    </div>
  );
}

export function DocumentosTab() {
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [searchTipoDoc, setSearchTipoDoc] = useState<string>('');
  const [searchDocumento, setSearchDocumento] = useState<string>('');
  const [filtroTipoDoc, setFiltroTipoDoc] = useState<string>('');
  const [filtroDocumento, setFiltroDocumento] = useState<string>('');
  const [expandido, setExpandido] = useState<string | null>(null);

  const filtrosActivos: boolean = !!filtroTipoDoc || !!filtroDocumento;

  const lista = useAsesoresConDocumentos({
    programa: PROGRAMA_MOVILIDAD_ID,
    page,
    page_size: pageSize,
    cedula: filtroDocumento || undefined,
    tipo_doc: filtroTipoDoc || undefined,
  });

  const handleBuscar = () => {
    setFiltroTipoDoc(searchTipoDoc);
    setFiltroDocumento(searchDocumento.trim());
    setPage(1);
  };

  const handleLimpiar = () => {
    setSearchTipoDoc('');
    setSearchDocumento('');
    setFiltroTipoDoc('');
    setFiltroDocumento('');
    setPage(1);
  };

  const totalPages: number = lista.data ? Math.max(1, Math.ceil(lista.data.total / pageSize)) : 1;

  return (
    <>
      <div className="d-flex align-items-center justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
        <small className="text-muted">
          {lista.data ? `${lista.data.total} ${filtrosActivos ? 'asesores encontrados' : 'asesores con documentos'}` : ''}
        </small>
        <Form.Select
          size="sm"
          style={{ width: 'auto' }}
          value={pageSize}
          onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}
        >
          {PAGE_SIZE_OPTIONS.map((size) => (
            <option key={size} value={size}>Ver {size} por página</option>
          ))}
        </Form.Select>
      </div>

      <div className="px-3 pb-3">
        <div className="d-flex align-items-end gap-2 flex-wrap p-3 rounded" style={{ background: '#f8f9fa', border: '1px solid #dee2e6' }}>
          <Form.Group style={{ minWidth: 160 }}>
            <Form.Label className="small mb-1 fw-semibold">Tipo de Documento</Form.Label>
            <Form.Select
              size="sm"
              value={searchTipoDoc}
              onChange={(e) => setSearchTipoDoc(e.target.value)}
            >
              <option value="">Todos</option>
              <option value="CC">C.C.</option>
              <option value="CE">C.E.</option>
              <option value="F&I">F&amp;I</option>
              <option value="GC">GC</option>
              <option value="PEP">PEP</option>
              <option value="PPT">PPT</option>
              <option value="VDA">VDA</option>
            </Form.Select>
          </Form.Group>
          <Form.Group style={{ minWidth: 180 }}>
            <Form.Label className="small mb-1 fw-semibold">Documento</Form.Label>
            <Form.Control
              size="sm"
              placeholder="Ej: 12345678"
              value={searchDocumento}
              onChange={(e) => setSearchDocumento(e.target.value.replace(/\D/g, ''))}
              maxLength={20}
            />
          </Form.Group>
          <Button
            variant="danger"
            size="sm"
            disabled={!searchTipoDoc && !searchDocumento}
            onClick={handleBuscar}
          >
            <i className="bi bi-search me-1" />Buscar
          </Button>
          <Button
            variant="outline-secondary"
            size="sm"
            onClick={handleLimpiar}
          >
            <i className="bi bi-x-circle me-1" />Limpiar
          </Button>
        </div>
      </div>

      {lista.isLoading ? (
        <div className="text-center py-5"><Spinner animation="border" variant="danger" /></div>
      ) : !lista.data || lista.data.items.length === 0 ? (
        <div className="text-center py-5 text-muted">
          <i className="bi bi-inbox fs-1 d-block mb-2" />
          Sin asesores con documentos
        </div>
      ) : (
        <Table hover responsive className="mb-0">
          <thead className="table-light">
            <tr>
              <th>Tipo de Documento</th>
              <th>Usuario</th>
              <th>Email</th>
              <th className="text-center">Operación</th>
            </tr>
          </thead>
          <tbody>
            {lista.data.items.map((item) => {
              const abierto: boolean = expandido === item.numero_documento;
              return (
                <Fragment key={item.numero_documento}>
                  <tr>
                    <td>{item.tipo_documento}</td>
                    <td className="font-monospace">{item.numero_documento}</td>
                    <td>{item.email ?? '—'}</td>
                    <td className="text-center">
                      <Button
                        variant={abierto ? 'secondary' : 'outline-danger'}
                        size="sm"
                        onClick={() => setExpandido(abierto ? null : item.numero_documento)}
                      >
                        <i className={`bi ${abierto ? 'bi-chevron-up' : 'bi-folder2-open'} me-1`} />
                        {abierto ? 'Cerrar' : 'Ver Documentación'}
                      </Button>
                    </td>
                  </tr>
                  {abierto && (
                    <tr>
                      <td colSpan={4} className="p-0">
                        <DocumentosAsesor numeroDocumento={item.numero_documento} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </Table>
      )}

      {lista.data && totalPages > 1 && (
        <div className="d-flex justify-content-center align-items-center gap-2 py-3">
          <Button variant="outline-secondary" size="sm" disabled={page === 1} onClick={() => setPage(1)}>
            <i className="bi bi-chevron-double-left" />
          </Button>
          <Button variant="outline-secondary" size="sm" disabled={page === 1} onClick={() => setPage((prev) => prev - 1)}>
            <i className="bi bi-chevron-left" />
          </Button>
          <span className="small">Página {page} de {totalPages}</span>
          <Button variant="outline-secondary" size="sm" disabled={page === totalPages} onClick={() => setPage((prev) => prev + 1)}>
            <i className="bi bi-chevron-right" />
          </Button>
          <Button variant="outline-secondary" size="sm" disabled={page === totalPages} onClick={() => setPage(totalPages)}>
            <i className="bi bi-chevron-double-right" />
          </Button>
        </div>
      )}
    </>
  );
}
