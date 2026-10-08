import { Link } from 'react-router-dom';
import { Alert, Badge, Card, Col, ProgressBar, Row, Spinner } from 'react-bootstrap';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../shared/api/client';
import { useAuthStore } from '../../entities/user/model/authStore';
import {
  useMiContacto,
  useMiDashboard,
} from '../../features/perfil-self/model/usePerfilSelf';
import type { MiDashboard } from '../../features/perfil-self/model/types';

function StageRow({
  label, ok, onLink,
}: { label: string; ok: boolean | null; onLink: string }) {
  if (ok === null) {
    return (
      <li className="d-flex align-items-center justify-content-between py-2 border-bottom">
        <span className="text-muted small">{label}</span>
        <Badge bg="light" text="dark">N/A</Badge>
      </li>
    );
  }
  return (
    <li className="d-flex align-items-center justify-content-between py-2 border-bottom">
      <span className={ok ? 'text-success' : 'text-muted'}>
        <i className={`bi ${ok ? 'bi-check-circle-fill' : 'bi-circle'} me-2`} />
        {label}
      </span>
      {ok ? (
        <Badge bg="success">Completo</Badge>
      ) : (
        <Link to={onLink} className="btn btn-sm btn-outline-danger">
          Completar <i className="bi bi-arrow-right ms-1" />
        </Link>
      )}
    </li>
  );
}

function badgeDocumento(info: { subido: boolean; estado: string | null; version: number }): string {
  if (info.estado?.toLowerCase() === 'aprobado') return 'success';
  if (info.estado?.toLowerCase() === 'revision') return 'info';
  if (info.subido) return 'warning';
  return 'secondary';
}

function DocumentoRow({
  label, info,
}: { label: string; info: { subido: boolean; estado: string | null; version: number } }) {
  const bg: string = badgeDocumento(info);
  return (
    <li className="d-flex align-items-center justify-content-between py-2 border-bottom">
      <span className={info.subido ? '' : 'text-muted'}>
        <i className={`bi ${info.subido ? 'bi-file-earmark-pdf-fill text-danger' : 'bi-file-earmark'} me-2`} />
        {label}
        {info.subido && info.version > 1 && (
          <span className="badge bg-light text-muted ms-2">v{info.version}</span>
        )}
      </span>
      <Badge bg={bg}>{info.subido ? (info.estado ?? 'pendiente') : 'Sin cargar'}</Badge>
    </li>
  );
}

function colorPorcentaje(porcentaje: number): 'success' | 'warning' | 'danger' {
  if (porcentaje >= 100) return 'success';
  if (porcentaje >= 50) return 'warning';
  return 'danger';
}

function extraerSubprogramaId(contacto: unknown): number | null {
  const contactoData = contacto as Record<string, unknown> | null | undefined;
  if (!contactoData) return null;
  const subRaw = contactoData.comisionista_subprograma_id;
  if (typeof subRaw === 'object' && subRaw !== null) {
    const cspid = (subRaw as Record<string, unknown>).cspid;
    return typeof cspid === 'number' ? cspid : null;
  }
  return typeof subRaw === 'number' ? subRaw : null;
}

interface Props {
  perfilRoute: string; // /perfil-movilidad o /perfil-consumo
}

export function MiDashboardComisionista({ perfilRoute }: Props) {
  const dash = useMiDashboard();
  const miContacto = useMiContacto();
  const sapinHabilitado = useAuthStore((state) => state.canAccessSapin());

  const esMovilidad: boolean = dash.data?.rol_principal === 'comisionista';

  const { data: subprogramasConsumo } = useQuery({
    queryKey: ['asesor-consumo-subprogramas', 2],
    queryFn: () => apiClient.get<{ cspid: number; cspid_nombre: string; cpid: number }[]>('/asesor-consumo/subprogramas/2').then(r => r.data),
    enabled: !esMovilidad,
    staleTime: Infinity,
  });

  if (dash.isLoading) {
    return <div className="text-center py-5"><Spinner animation="border" variant="danger" /></div>;
  }
  if (dash.isError || !dash.data) {
    return <Alert variant="danger">No se pudo cargar tu dashboard.</Alert>;
  }

  const d: MiDashboard = dash.data;
  const porcentaje: number = d.perfil.porcentaje_completado;
  const porcentajeColor = colorPorcentaje(porcentaje);

  // Nombres pre-resueltos por el backend (con fallback al valor raw).
  const departamentoNombre: string | null = d.departamento_nombre ?? d.departamento;
  const ciudadNombre: string | null = d.ciudad_nombre ?? d.ciudad;

  const subprogramaId: number | null = extraerSubprogramaId(miContacto.data);
  const subprogramaNombre: string | null = subprogramaId !== null
    ? subprogramasConsumo?.find((sub) => sub.cspid === subprogramaId)?.cspid_nombre ?? null
    : null;

  const renderSaludo = () => (
    <Card className="shadow-sm border-0 mb-4">
      <Card.Body className="p-4">
        <Row className="align-items-center">
          <Col md={8}>
            <h3 className="fw-bold mb-1">Hola, {d.nombre_completo || d.numero_documento}</h3>
            <div className="text-muted">
              <Badge bg="dark" className="me-2">
                <i className={`bi ${esMovilidad ? 'bi-car-front-fill' : 'bi-bag-fill'} me-1`} />
                {d.programa?.nombre ?? (esMovilidad ? 'Movilidad' : 'Consumo y Servicios')}
              </Badge>
              Documento: <span className="font-monospace">{d.numero_documento}</span>
            </div>
          </Col>
          <Col md={4}>
            <div className="text-end">
              <div className="text-muted small fw-semibold mb-1">Tu perfil está {porcentaje}% completo</div>
              <ProgressBar
                now={porcentaje}
                variant={porcentajeColor}
                label={`${d.perfil.stages_completos}/${d.perfil.stages_total}`}
                style={{ height: 12 }}
              />
            </div>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );

  const renderPerfilCard = () => (
    <Col md={6} lg={esMovilidad ? 4 : 6}>
      <Card className="shadow-sm border-0 h-100">
        <Card.Header className="bg-white border-bottom-0 pt-3 pb-0">
          <h6 className="fw-bold mb-0"><i className="bi bi-person-vcard-fill text-danger me-2" />Mi Perfil</h6>
        </Card.Header>
        <Card.Body>
          <ul className="list-unstyled mb-3">
            <StageRow label="Datos de contacto" ok={d.perfil.contacto_completo} onLink={perfilRoute} />
            {esMovilidad && (
              <StageRow label="Datos tributarios" ok={d.perfil.tributario_completo} onLink={perfilRoute} />
            )}
            <StageRow label="Perfil emocional" ok={d.perfil.emocional_completo} onLink={perfilRoute} />
          </ul>
          <Link to={perfilRoute} className="btn btn-danger btn-sm w-100">
            <i className="bi bi-pencil-square me-1" />Editar mi perfil
          </Link>
        </Card.Body>
      </Card>
    </Col>
  );

  const renderDocumentosCard = () => {
    if (!esMovilidad || !d.documentos) return null;
    return (
      <Col md={6} lg={4}>
        <Card className="shadow-sm border-0 h-100">
          <Card.Header className="bg-white border-bottom-0 pt-3 pb-0 d-flex justify-content-between align-items-center">
            <h6 className="fw-bold mb-0"><i className="bi bi-folder2-open text-danger me-2" />Mis Documentos</h6>
            <span className="text-muted small">{d.documentos.total_subidos}/{d.documentos.total_esperados}</span>
          </Card.Header>
          <Card.Body>
            <ul className="list-unstyled mb-3">
              <DocumentoRow label="Cédula" info={d.documentos.items.cedula} />
              <DocumentoRow label="RUT" info={d.documentos.items.rut} />
              <DocumentoRow label="Contrato" info={d.documentos.items.contrato} />
            </ul>
            <Link to={`${perfilRoute}#documentos`} className="btn btn-outline-danger btn-sm w-100">
              <i className="bi bi-upload me-1" />Gestionar mis documentos
            </Link>
          </Card.Body>
        </Card>
      </Col>
    );
  };

  const renderSapinCard = () => (
    <Col md={6} lg={esMovilidad ? 4 : 6}>
      <Card className="shadow-sm border-0 h-100">
        <Card.Header className="bg-white border-bottom-0 pt-3 pb-0">
          <h6 className="fw-bold mb-0"><i className="bi bi-gift-fill text-warning me-2" />SAPIN / Incentivos</h6>
        </Card.Header>
        <Card.Body>
          <div className="text-center py-2">
            {sapinHabilitado && d.incentivos_habilitados ? (
              <>
                <i className="bi bi-check-circle-fill text-success display-5 d-block mb-2" />
                <p className="mb-3 fw-semibold">Tienes acceso a incentivos</p>
                <Link to="/sapin" className="btn btn-warning btn-sm">Ir a SAPIN <i className="bi bi-arrow-right ms-1" /></Link>
              </>
            ) : (
              <>
                <i className="bi bi-info-circle-fill text-muted display-5 d-block mb-2" />
                <p className="text-muted mb-0">
                  {d.incentivos_habilitados
                    ? 'SAPIN aún no está habilitado para tu usuario.'
                    : 'Tu perfil no tiene incentivos asignados.'}
                </p>
              </>
            )}
          </div>
        </Card.Body>
      </Card>
    </Col>
  );

  const renderDatosClave = () => (
    <Col xs={12}>
      <Card className="shadow-sm border-0">
        <Card.Header className="bg-white border-bottom-0 pt-3 pb-0">
          <h6 className="fw-bold mb-0"><i className="bi bi-info-square text-danger me-2" />Mis datos clave</h6>
        </Card.Header>
        <Card.Body>
          <Row className="g-3">
            <Col md={3}>
              <div className="text-muted small fw-semibold">Celular</div>
              <div className="font-monospace">{d.celular ?? '—'}</div>
            </Col>
            <Col md={4}>
              <div className="text-muted small fw-semibold">Email</div>
              <div>{d.email ?? '—'}</div>
            </Col>
            <Col md={esMovilidad ? 3 : 2}>
              <div className="text-muted small fw-semibold">Departamento</div>
              <div>{departamentoNombre ?? '—'}</div>
            </Col>
            <Col md={2}>
              <div className="text-muted small fw-semibold">Ciudad</div>
              <div>{ciudadNombre ?? '—'}</div>
            </Col>
            {!esMovilidad && (
              <Col md={3}>
                <div className="text-muted small fw-semibold">Subprograma</div>
                <div>{subprogramaNombre ?? '—'}</div>
              </Col>
            )}
            {d.direccion && (
              <Col xs={12}>
                <div className="text-muted small fw-semibold">Dirección</div>
                <div>{d.direccion}</div>
              </Col>
            )}
          </Row>
        </Card.Body>
      </Card>
    </Col>
  );

  return (
    <div className="container-fluid py-3">
      {renderSaludo()}
      <Row className="g-4">
        {renderPerfilCard()}
        {renderDocumentosCard()}
        {renderSapinCard()}
        {renderDatosClave()}
      </Row>
    </div>
  );
}
