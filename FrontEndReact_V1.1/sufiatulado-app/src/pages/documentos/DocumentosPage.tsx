import { useState } from 'react';
import { Card, Table, Button, Badge, Form, InputGroup } from 'react-bootstrap';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../shared/api/client';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { LoadingSpinner } from '../../shared/ui/components/LoadingSpinner';
import { EmptyState } from '../../shared/ui/components/EmptyState';
import { TIPO_DOCUMENTO, QUERY_KEYS } from '../../shared/config/constants';
import { formatDate } from '../../shared/lib/formatters';

interface Documento {
  id: number;
  numero_documento: string;
  tipo: number;
  nombre_archivo: string | null;
  url: string | null;
  created: number;
}

const TIPO_LABELS: Record<number, string> = {
  [TIPO_DOCUMENTO.CEDULA]: 'Cédula',
  [TIPO_DOCUMENTO.RUT]: 'RUT',
  [TIPO_DOCUMENTO.CONTRATO]: 'Contrato',
};

export function DocumentosPage() {
  const [busqueda, setBusqueda] = useState('');

  const { data: documentos, isLoading } = useQuery<Documento[]>({
    queryKey: [QUERY_KEYS.DOCUMENTOS, busqueda],
    queryFn: async () => {
      const { data } = await apiClient.get<Documento[]>('/documentos', {
        params: busqueda ? { documento: busqueda } : undefined,
      });
      return data;
    },
  });

  return (
    <div>
      <PageHeader
        title="Documentos"
        subtitle="Gestión de documentos por comisionista"
        icon="bi-file-earmark-text"
        actions={
          <Button variant="primary" size="sm">
            <i className="bi bi-upload me-2" />
            Subir documento
          </Button>
        }
      />

      <Card className="shadow-sm" style={{ border: 'none' }}>
        <Card.Header className="bg-white border-0 pt-4 pb-0 px-4">
          <InputGroup style={{ maxWidth: 360 }}>
            <InputGroup.Text className="bg-light border-end-0">
              <i className="bi bi-search text-muted" />
            </InputGroup.Text>
            <Form.Control
              placeholder="Buscar por cédula..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="border-start-0"
            />
          </InputGroup>
        </Card.Header>
        <Card.Body className="p-0">
          {isLoading ? (
            <LoadingSpinner fullPage />
          ) : !documentos?.length ? (
            <EmptyState icon="bi-file-earmark" title="Sin documentos" description="No se encontraron documentos." />
          ) : (
            <div className="table-responsive">
              <Table hover className="mb-0">
                <thead>
                  <tr>
                    <th>Documento</th>
                    <th>Tipo</th>
                    <th>Archivo</th>
                    <th>Fecha</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {documentos.map((doc) => (
                    <tr key={doc.id}>
                      <td className="font-monospace">{doc.numero_documento}</td>
                      <td>
                        <Badge
                          bg={doc.tipo === TIPO_DOCUMENTO.CONTRATO ? 'primary' : doc.tipo === TIPO_DOCUMENTO.RUT ? 'info' : 'secondary'}
                          className="bg-opacity-15 text-body"
                        >
                          {TIPO_LABELS[doc.tipo] ?? `Tipo ${doc.tipo}`}
                        </Badge>
                      </td>
                      <td>{doc.nombre_archivo ?? '—'}</td>
                      <td>{formatDate(String(doc.created))}</td>
                      <td>
                        {doc.url && (
                          <a
                            href={doc.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn btn-sm btn-outline-primary"
                          >
                            <i className="bi bi-download" />
                          </a>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}
