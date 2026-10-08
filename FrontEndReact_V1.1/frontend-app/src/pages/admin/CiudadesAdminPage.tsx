import { useEffect, useState, useMemo } from 'react';
import { Alert, Button, Card, Form, Nav, Spinner, Table } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { ConfirmModal } from '../../shared/ui/components/ConfirmModal';
import { extractError } from '../../shared/lib/extractError';
import {
  useActualizarAdminCiudad,
  useAdminCiudadesList,
  useCrearAdminCiudad,
  useEliminarAdminCiudad,
} from '../../features/admin-ciudades/model/useAdminCiudades';
import type {
  AdminCiudadFormPayload,
  AdminCiudadListItem,
} from '../../features/admin-ciudades/model/types';
import { useAdminDepartamentosList } from '../../features/admin-departamentos/model/useAdminDepartamentos';

type Tab = 'lista' | 'registro';
const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

interface FormState { ciudad: string; did: string }
const initForm: FormState = { ciudad: '', did: '' };

export function CiudadesAdminPage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState<Tab>('lista');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [searchNombre, setSearchNombre] = useState<string>('');
  const [searchDid, setSearchDid] = useState<string>('');
  const [filtroNombre, setFiltroNombre] = useState<string>('');
  const [filtroDid, setFiltroDid] = useState<string>('');
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<FormState>(initForm);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  const departamentosQ = useAdminDepartamentosList({ page: 1, page_size: 100 });
  const lista = useAdminCiudadesList({
    page,
    page_size: pageSize,
    nombre: filtroNombre || undefined,
    did: filtroDid ? Number(filtroDid) : undefined,
  });
  const crearMut = useCrearAdminCiudad();
  const actualizarMut = useActualizarAdminCiudad();
  const eliminarMut = useEliminarAdminCiudad();

  const filtrosActivos: boolean = !!filtroNombre || !!filtroDid;
  const totalPages: number = lista.data ? Math.max(1, Math.ceil(lista.data.total / pageSize)) : 1;
  const isEditing: boolean = editId !== null;
  const isSaving: boolean = crearMut.isPending || actualizarMut.isPending;
  const departamentos = departamentosQ.data?.items ?? [];

  const departamentoPorDid: Map<number, string> = useMemo(() => {
    const m = new Map<number, string>();
    (departamentosQ.data?.items ?? []).forEach((d) => m.set(d.did, d.departamento));
    return m;
  }, [departamentosQ.data]);

  useEffect(() => {
    if (!success) return;
    const t = setTimeout(() => setSuccess(''), 3500);
    return () => clearTimeout(t);
  }, [success]);
  useEffect(() => { if (tab !== 'registro') setError(''); }, [tab]);

  const aplicarFiltros = () => { setFiltroNombre(searchNombre.trim()); setFiltroDid(searchDid); setPage(1); };
  const limpiarFiltros = () => { setSearchNombre(''); setSearchDid(''); setFiltroNombre(''); setFiltroDid(''); setPage(1); };

  const handleNuevo = () => { setEditId(null); setForm(initForm); setError(''); setTab('registro'); };
  const handleCancelar = () => { setEditId(null); setForm(initForm); setError(''); setTab('lista'); };

  const handleEditar = (item: AdminCiudadListItem) => {
    setEditId(item.cid);
    setForm({ ciudad: item.ciudad, did: item.did !== null ? String(item.did) : '' });
    setError('');
    setTab('registro');
  };

  const handleGuardar = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!form.ciudad.trim()) { setError('El nombre de la ciudad es obligatorio'); return; }
    const payload: AdminCiudadFormPayload = {
      ciudad: form.ciudad.trim(),
      did: form.did.trim() === '' ? null : Number(form.did),
    };
    try {
      if (isEditing && editId !== null) {
        await actualizarMut.mutateAsync({ cid: editId, payload });
      } else {
        await crearMut.mutateAsync(payload);
      }
      handleCancelar();
      setSuccess(isEditing ? 'Ciudad actualizada correctamente' : 'Ciudad creada correctamente');
    } catch (err) { setError(extractError(err, 'Error al guardar la ciudad')); }
  };

  const handleConfirmDelete = async () => {
    if (confirmDeleteId === null) return;
    try {
      await eliminarMut.mutateAsync(confirmDeleteId);
      setSuccess('Ciudad eliminada correctamente');
    } catch (err) {
      setError(extractError(err, 'Error al eliminar la ciudad'));
    } finally {
      setConfirmDeleteId(null);
    }
  };

  const renderTabla = () => {
    if (lista.isLoading) return <div className="text-center py-5"><Spinner animation="border" /></div>;
    if (lista.isError) return <Alert variant="danger" className="m-3">Error al cargar las ciudades</Alert>;
    if (!lista.data || lista.data.items.length === 0) {
      return (
        <div className="text-center py-5 text-muted">
          <i className="bi bi-inbox display-4 d-block mb-2" />No se encontraron ciudades
        </div>
      );
    }
    return (
      <>
        <Table hover responsive className="mb-0 align-middle">
          <thead className="table-light">
            <tr>
              <th style={{ width: 100 }}>Código</th>
              <th>Nombre</th>
              <th style={{ width: 220 }}>Departamento</th>
              <th className="text-end" style={{ width: 180 }}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {lista.data.items.map((c) => {
              const depNombre = c.did !== null ? departamentoPorDid.get(c.did) : undefined;
              return (
                <tr key={c.cid}>
                  <td><code>{c.cid}</code></td>
                  <td className="fw-semibold">{c.ciudad}</td>
                  <td>{depNombre ?? (c.did !== null ? <code className="small">did={c.did}</code> : <span className="text-muted small">—</span>)}</td>
                  <td className="text-end">
                    <Button size="sm" variant="outline-primary" className="me-1" onClick={() => handleEditar(c)}>
                      <i className="bi bi-pencil-fill" />
                    </Button>
                    <Button size="sm" variant="outline-danger" onClick={() => setConfirmDeleteId(c.cid)}>
                      <i className="bi bi-trash-fill" />
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </Table>
        <div className="d-flex align-items-center justify-content-between px-3 py-3 border-top">
          <div className="text-muted small">
            Página <strong>{page}</strong> de <strong>{totalPages}</strong> — {lista.data.total} resultados
          </div>
          <div className="d-flex gap-2">
            <Button size="sm" variant="outline-secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>
              <i className="bi bi-chevron-left me-1" />Anterior
            </Button>
            <Button size="sm" variant="outline-secondary" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
              Siguiente<i className="bi bi-chevron-right ms-1" />
            </Button>
          </div>
        </div>
      </>
    );
  };

  const renderLista = () => (
    <>
      {success && (
        <div className="px-3 pt-3">
          <Alert variant="success" dismissible onClose={() => setSuccess('')} className="mb-0">
            <i className="bi bi-check-circle me-2" />{success}
          </Alert>
        </div>
      )}
      <div className="d-flex align-items-center justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
        <div className="d-flex align-items-end gap-2 flex-wrap">
          <Form.Group style={{ minWidth: 200 }}>
            <Form.Label className="small mb-1">Nombre</Form.Label>
            <Form.Control
              size="sm" type="text" placeholder="Filtrar por nombre..."
              value={searchNombre}
              onChange={(e) => setSearchNombre(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') aplicarFiltros(); }}
              maxLength={50}
            />
          </Form.Group>
          <Form.Group style={{ minWidth: 200 }}>
            <Form.Label className="small mb-1">Departamento</Form.Label>
            <Form.Select size="sm" value={searchDid} onChange={(e) => setSearchDid(e.target.value)}>
              <option value="">Todos</option>
              {departamentos.map((d) => <option key={d.did} value={d.did}>{d.departamento}</option>)}
            </Form.Select>
          </Form.Group>
          <Button size="sm" variant="primary" onClick={aplicarFiltros}><i className="bi bi-search me-1" />Buscar</Button>
          {filtrosActivos && (
            <Button size="sm" variant="outline-secondary" onClick={limpiarFiltros}>
              <i className="bi bi-x-circle me-1" />Limpiar
            </Button>
          )}
        </div>
        <div className="d-flex align-items-end gap-2">
          <Form.Group style={{ minWidth: 80 }}>
            <Form.Label className="small mb-1">Mostrar</Form.Label>
            <Form.Select size="sm" value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}>
              {PAGE_SIZE_OPTIONS.map((n) => <option key={n} value={n}>{n}</option>)}
            </Form.Select>
          </Form.Group>
          <Button size="sm" variant="success" onClick={handleNuevo}><i className="bi bi-plus-lg me-1" />Nueva Ciudad</Button>
        </div>
      </div>
      {renderTabla()}
    </>
  );

  const renderRegistro = () => (
    <Form onSubmit={handleGuardar} noValidate>
      {success && (<Alert variant="success" className="mb-3"><i className="bi bi-check-circle me-2" />{success}</Alert>)}
      {error && (<Alert variant="danger" className="mb-3"><i className="bi bi-exclamation-triangle me-2" />{error}</Alert>)}
      {isEditing && editId !== null && (<div className="mb-3 text-muted small">Editando ciudad con código <code>{editId}</code></div>)}
      <div className="row g-3">
        <div className="col-md-6">
          <Form.Group>
            <Form.Label>Nombre <span className="text-danger">*</span></Form.Label>
            <Form.Control
              type="text" maxLength={50} value={form.ciudad}
              onChange={(e) => setForm((p) => ({ ...p, ciudad: e.target.value }))}
              required autoFocus placeholder="Ej: MEDELLIN"
            />
          </Form.Group>
        </div>
        <div className="col-md-6">
          <Form.Group>
            <Form.Label>Departamento</Form.Label>
            <Form.Select value={form.did} onChange={(e) => setForm((p) => ({ ...p, did: e.target.value }))}>
              <option value="">Sin asignar</option>
              {departamentos.map((d) => <option key={d.did} value={d.did}>{d.departamento}</option>)}
            </Form.Select>
          </Form.Group>
        </div>
      </div>
      <div className="d-flex justify-content-end gap-2 mt-4">
        <Button type="button" variant="outline-secondary" onClick={handleCancelar} disabled={isSaving}>
          <i className="bi bi-x-circle me-1" />Cancelar
        </Button>
        <Button type="submit" variant="primary" disabled={isSaving}>
          {isSaving ? (<><Spinner size="sm" className="me-1" />Guardando…</>) : (<><i className="bi bi-check-circle me-1" />{isEditing ? 'Actualizar' : 'Crear'}</>)}
        </Button>
      </div>
    </Form>
  );

  return (
    <div>
      <PageHeader
        title="Administrar Ciudades"
        subtitle={lista.data ? `${lista.data.total} ciudades${filtrosActivos ? ' encontradas' : ''}` : undefined}
        icon="bi-geo-alt-fill"
      />
      <div className="mb-3">
        <Button size="sm" variant="outline-secondary" onClick={() => navigate('/admin/catalogos')}>
          <i className="bi bi-arrow-left me-1" />Volver
        </Button>
      </div>

      <Card className="border-0 shadow-sm">
        <Card.Header className="bg-white border-bottom-0 pb-0">
          <Nav variant="tabs" activeKey={tab} onSelect={(k) => k && setTab(k as Tab)}>
            <Nav.Item><Nav.Link eventKey="lista"><i className="bi bi-list-ul me-2" />Lista de Ciudades</Nav.Link></Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="registro">
                <i className={`bi ${isEditing ? 'bi-pencil-square' : 'bi-plus-circle'} me-2`} />
                {isEditing ? 'Editar Ciudad' : 'Nueva Ciudad'}
              </Nav.Link>
            </Nav.Item>
          </Nav>
        </Card.Header>
        <Card.Body className={tab === 'lista' ? 'p-0' : 'p-4'}>
          {tab === 'lista' && renderLista()}
          {tab === 'registro' && renderRegistro()}
        </Card.Body>
      </Card>

      <ConfirmModal
        show={confirmDeleteId !== null}
        title="Eliminar Ciudad"
        message={<>¿Confirma eliminar la ciudad? Esta acción es <strong>permanente</strong>.<br />
          <small className="text-muted">Si está referenciada en perfiles de contacto, la operación será rechazada.</small></>}
        confirmLabel="Eliminar"
        confirmIcon="bi-trash-fill"
        confirmVariant="danger"
        loading={eliminarMut.isPending}
        loadingLabel="Eliminando…"
        onConfirm={handleConfirmDelete}
        onHide={() => setConfirmDeleteId(null)}
      />
    </div>
  );
}
