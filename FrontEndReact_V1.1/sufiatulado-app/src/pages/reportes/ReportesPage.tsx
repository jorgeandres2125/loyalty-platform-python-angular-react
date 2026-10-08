import { useEffect, useMemo, useState } from 'react';
import { Alert, Button, ButtonGroup, Card, Col, Form, Row, Spinner, Table } from 'react-bootstrap';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../shared/api/client';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { PROGRAMA, QUERY_KEYS } from '../../shared/config/constants';
import { useGenerarReporte, useObtenerPreviewReporte } from '../../features/reportes/model/useReportes';
import { REPORTE_TIPO, type ReporteTipo } from '../../features/reportes/model/types';
import type { Subprograma } from '../../shared/api/catalogos';

interface FormState {
  tipo: ReporteTipo;
  programa: number;
  subprograma: number | '';
  fecha_inicio: string;
  fecha_fin: string;
  cedula: string;
  estado: number | '';
}

const TIPOS_REPORTE: ReadonlyArray<{ value: ReporteTipo; label: string }> = [
  { value: REPORTE_TIPO.HOJA_VIDA, label: 'Hoja de vida' },
  { value: REPORTE_TIPO.INFO_LABORAL, label: 'Información laboral' },
  { value: REPORTE_TIPO.PLANTILLA_PARTICIPANTES, label: 'Plantilla participantes' },
  { value: REPORTE_TIPO.INFO_TRIBUTARIA, label: 'Información tributaria' },
  { value: REPORTE_TIPO.USUARIOS_MIGRADOS, label: 'Usuarios migrados' },
  { value: REPORTE_TIPO.DEFAULT, label: 'Listado básico' },
  { value: REPORTE_TIPO.ESTADOS_PERFILES, label: 'Estados de perfiles' },
];

const ESTADOS_PERFIL: ReadonlyArray<{ value: number; label: string }> = [
  { value: 3, label: 'Todos' },
  { value: 0, label: 'Incompleto' },
  { value: 1, label: 'Completo' },
  { value: 2, label: 'Pendiente por documentación' },
];

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

function renderCell(value: string | number | boolean | null): string {
  if (value === null || value === undefined) return '';
  if (typeof value === 'boolean') return value ? 'Sí' : 'No';
  return String(value);
}

export function ReportesPage() {
  const [params, setParams] = useState<FormState>({
    tipo: REPORTE_TIPO.HOJA_VIDA,
    programa: PROGRAMA.MOVILIDAD,
    subprograma: '',
    fecha_inicio: '',
    fecha_fin: '',
    cedula: '',
    estado: '',
  });

  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);

  const ocultarPrograma: boolean = useMemo(() => {
    const tiposSinPrograma: readonly ReporteTipo[] = [
      REPORTE_TIPO.INFO_LABORAL,
      REPORTE_TIPO.INFO_TRIBUTARIA,
      REPORTE_TIPO.USUARIOS_MIGRADOS,
    ];
    return tiposSinPrograma.includes(params.tipo);
  }, [params.tipo]);
  const mostrarEstadoYCedula: boolean = params.tipo === REPORTE_TIPO.ESTADOS_PERFILES;
  const fechasObligatorias: boolean = true;
  const [errorFechas, setErrorFechas] = useState<string>('');

  const subprogramasQuery = useQuery({
    queryKey: [QUERY_KEYS.REPORTES, 'subprogramas', params.programa],
    queryFn: async () => {
      const url: string = `/asesor-consumo/subprogramas/${params.programa}`;
      const { data } = await apiClient.get<Subprograma[]>(url);
      return data;
    },
    enabled: !ocultarPrograma && params.programa === PROGRAMA.CONSUMO,
  });

  useEffect(() => {
    setParams((prev) => ({ ...prev, subprograma: '' }));
  }, [params.programa, params.tipo]);

  const generar = useGenerarReporte();
  const preview = useObtenerPreviewReporte();

  useEffect(() => {
    if (!generar.isSuccess) return;
    const timeoutId = setTimeout(() => generar.reset(), 10_000);
    return () => clearTimeout(timeoutId);
  }, [generar.isSuccess, generar.reset]);

  const totalPages: number = preview.data
    ? Math.max(1, Math.ceil(preview.data.total / preview.data.page_size))
    : 1;

  const validarFechas = (): boolean => {
    setErrorFechas('');
    if (!fechasObligatorias) return true;
    if (!params.fecha_inicio || !params.fecha_fin) {
      setErrorFechas('Selecciona fecha inicio y fecha fin.');
      return false;
    }
    if (params.fecha_inicio >= params.fecha_fin) {
      setErrorFechas('La fecha inicio debe ser menor que la fecha fin.');
      return false;
    }
    return true;
  };

  const buildBaseParams = () => ({
    tipo: params.tipo,
    programa: ocultarPrograma ? 1 : params.programa,
    subprograma: ocultarPrograma ? null : (params.subprograma === '' ? null : Number(params.subprograma)),
    fecha_inicio: params.fecha_inicio || undefined,
    fecha_fin: params.fecha_fin || undefined,
    cedula: mostrarEstadoYCedula && params.cedula ? params.cedula : undefined,
    estado: mostrarEstadoYCedula && params.estado !== '' ? Number(params.estado) : undefined,
  });

  const handleGenerarExcel = (e: React.FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    if (!validarFechas()) return;
    generar.mutate(buildBaseParams());
  };

  const handleGenerarPreview = (): void => {
    if (!validarFechas()) return;
    setPage(1);
    preview.mutate({ ...buildBaseParams(), page: 1, page_size: pageSize });
  };

  const cambiarPagina = (nuevaPagina: number): void => {
    if (nuevaPagina < 1 || nuevaPagina > totalPages) return;
    setPage(nuevaPagina);
    preview.mutate({ ...buildBaseParams(), page: nuevaPagina, page_size: pageSize });
  };

  const cambiarPageSize = (nuevoSize: number): void => {
    setPageSize(nuevoSize);
    setPage(1);
    preview.mutate({ ...buildBaseParams(), page: 1, page_size: nuevoSize });
  };

  const subprogramaDisabled: boolean =
    params.programa === PROGRAMA.MOVILIDAD
    || subprogramasQuery.isLoading
    || (subprogramasQuery.data?.length ?? 0) === 0;

  const renderConfigForm = () => (
    <Card className="shadow-sm mb-3" style={{ border: 'none' }}>
      <Card.Body className="p-4">
        <Form onSubmit={handleGenerarExcel}>
          <h6 className="fw-bold mb-3 text-sufi-navy">Configurar reporte</h6>

          {generar.isError && (
            <Alert variant="danger" className="py-2">
              <i className="bi bi-exclamation-circle me-2" />
              Error al generar el reporte. Verifica los filtros e intenta de nuevo.
            </Alert>
          )}
          {generar.isSuccess && (
            <Alert variant="success" className="py-2">
              <i className="bi bi-check-circle me-2" />
              Reporte generado y descargado correctamente.
            </Alert>
          )}
          {preview.isError && (
            <Alert variant="danger" className="py-2">
              <i className="bi bi-exclamation-circle me-2" />
              Error al obtener la vista previa. Verifica los filtros e intenta de nuevo.
            </Alert>
          )}

          <Row className="g-3">
            <Col md={6}>
              <Form.Group>
                <Form.Label>Tipo de reporte</Form.Label>
                <Form.Select
                  value={params.tipo}
                  onChange={(e) => setParams((prev) => ({ ...prev, tipo: Number(e.target.value) as ReporteTipo }))}
                >
                  {TIPOS_REPORTE.map((tipoReporte) => (
                    <option key={tipoReporte.value} value={tipoReporte.value}>{tipoReporte.label}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>

            {!ocultarPrograma && (
              <Col md={6}>
                <Form.Group>
                  <Form.Label>Programa</Form.Label>
                  <Form.Select
                    value={params.programa}
                    onChange={(e) => setParams((prev) => ({ ...prev, programa: Number(e.target.value) }))}
                  >
                    <option value={PROGRAMA.MOVILIDAD}>Movilidad (Vehículos)</option>
                    <option value={PROGRAMA.CONSUMO}>Consumo y Servicios</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            )}

            {!ocultarPrograma && (
              <Col md={6}>
                <Form.Group>
                  <Form.Label>Subprograma</Form.Label>
                  <Form.Select
                    value={params.subprograma}
                    onChange={(e) => setParams((prev) => ({ ...prev, subprograma: e.target.value === '' ? '' : Number(e.target.value) }))}
                    disabled={subprogramaDisabled}
                  >
                    <option value="">Todos</option>
                    {(subprogramasQuery.data ?? []).map((subprograma) => (
                      <option key={subprograma.cspid} value={subprograma.cspid}>{subprograma.cspid_nombre}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            )}

            <Col xs={12} md={6}>
              <Row className="g-2">
                <Col xs={12} md={6}>
                  <Form.Group>
                    <Form.Label>
                      Fecha inicio
                      {fechasObligatorias && <span className="text-danger ms-1">*</span>}
                    </Form.Label>
                    <Form.Control
                      type="date"
                      value={params.fecha_inicio}
                      max={params.fecha_fin || undefined}
                      required={fechasObligatorias}
                      onChange={(e) => setParams((prev) => ({ ...prev, fecha_inicio: e.target.value }))}
                    />
                  </Form.Group>
                </Col>
                <Col xs={12} md={6}>
                  <Form.Group>
                    <Form.Label>
                      Fecha fin
                      {fechasObligatorias && <span className="text-danger ms-1">*</span>}
                    </Form.Label>
                    <Form.Control
                      type="date"
                      value={params.fecha_fin}
                      min={params.fecha_inicio || undefined}
                      required={fechasObligatorias}
                      onChange={(e) => setParams((prev) => ({ ...prev, fecha_fin: e.target.value }))}
                    />
                  </Form.Group>
                </Col>
              </Row>
            </Col>
            {errorFechas && (
              <Col xs={12}>
                <Alert variant="warning" className="py-2 mb-0">
                  <i className="bi bi-exclamation-triangle me-2" />{errorFechas}
                </Alert>
              </Col>
            )}

            {mostrarEstadoYCedula && (
              <>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Cédula</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="Solo dígitos"
                      value={params.cedula}
                      onChange={(e) => setParams((prev) => ({ ...prev, cedula: e.target.value.replace(/\D/g, '') }))}
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Estado</Form.Label>
                    <Form.Select
                      value={params.estado}
                      onChange={(e) => setParams((prev) => ({ ...prev, estado: e.target.value === '' ? '' : Number(e.target.value) }))}
                    >
                      <option value="">Todos</option>
                      {ESTADOS_PERFIL.filter((estado) => estado.value !== 3).map((estado) => (
                        <option key={estado.value} value={estado.value}>{estado.label}</option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>
              </>
            )}
          </Row>

          <div className="mt-4 d-flex flex-wrap gap-2">
            <Button type="button" variant="primary" onClick={handleGenerarPreview} disabled={preview.isPending}>
              {preview.isPending ? (
                <><Spinner size="sm" animation="border" className="me-2" />Generando…</>
              ) : (
                <><i className="bi bi-eye me-2" />Generar</>
              )}
            </Button>
            <Button type="submit" variant="success" disabled={generar.isPending}>
              {generar.isPending ? (
                <><Spinner size="sm" animation="border" className="me-2" />Descargando…</>
              ) : (
                <><i className="bi bi-file-earmark-excel me-2" />Descargar Excel</>
              )}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );

  const renderFilas = () => {
    if (!preview.data) return null;
    if (preview.data.rows.length === 0) {
      return (
        <tr>
          <td colSpan={preview.data.columns.length} className="text-center text-muted py-4">
            Sin resultados para los filtros seleccionados.
          </td>
        </tr>
      );
    }
    return preview.data.rows.map((row, i) => (
      <tr key={i}>
        {row.map((cell, j) => <td key={j} className="text-nowrap">{renderCell(cell)}</td>)}
      </tr>
    ));
  };

  const renderPreview = () => {
    if (!preview.data) return null;
    return (
      <Card className="shadow-sm" style={{ border: 'none' }}>
        <Card.Body className="p-4">
          <div className="d-flex flex-wrap justify-content-between align-items-center mb-3 gap-2">
            <h6 className="fw-bold mb-0 text-sufi-navy">
              Vista previa
              <span className="text-muted ms-2 fw-normal">
                ({preview.data.total} resultado{preview.data.total === 1 ? '' : 's'})
              </span>
            </h6>
            <div className="d-flex align-items-center gap-2">
              <Form.Label className="mb-0 small text-muted">Filas por página:</Form.Label>
              <Form.Select
                size="sm" style={{ width: 'auto' }} value={pageSize}
                onChange={(e) => cambiarPageSize(Number(e.target.value))}
                disabled={preview.isPending}
              >
                {PAGE_SIZE_OPTIONS.map((opt) => <option key={opt} value={opt}>{opt}</option>)}
              </Form.Select>
            </div>
          </div>

          <div className="table-responsive" style={{ maxHeight: '60vh' }}>
            <Table striped hover size="sm" className="mb-0">
              <thead className="position-sticky top-0 bg-light" style={{ zIndex: 1 }}>
                <tr>
                  {preview.data.columns.map((col) => <th key={col} className="text-nowrap">{col}</th>)}
                </tr>
              </thead>
              <tbody>{renderFilas()}</tbody>
            </Table>
          </div>

          {preview.data.total > 0 && (
            <div className="d-flex flex-wrap justify-content-between align-items-center mt-3 gap-2">
              <span className="text-muted small">Página {page} de {totalPages}</span>
              <ButtonGroup size="sm">
                <Button variant="outline-secondary" onClick={() => cambiarPagina(1)} disabled={page <= 1 || preview.isPending}>
                  <i className="bi bi-chevron-double-left" />
                </Button>
                <Button variant="outline-secondary" onClick={() => cambiarPagina(page - 1)} disabled={page <= 1 || preview.isPending}>
                  <i className="bi bi-chevron-left" />
                </Button>
                <Button variant="outline-secondary" onClick={() => cambiarPagina(page + 1)} disabled={page >= totalPages || preview.isPending}>
                  <i className="bi bi-chevron-right" />
                </Button>
                <Button variant="outline-secondary" onClick={() => cambiarPagina(totalPages)} disabled={page >= totalPages || preview.isPending}>
                  <i className="bi bi-chevron-double-right" />
                </Button>
              </ButtonGroup>
            </div>
          )}
        </Card.Body>
      </Card>
    );
  };

  return (
    <div>
      <PageHeader
        title="Reportes"
        subtitle="Genera vista previa o descarga en Excel"
        icon="bi-file-earmark-bar-graph"
      />
      {renderConfigForm()}
      {renderPreview()}
    </div>
  );
}
