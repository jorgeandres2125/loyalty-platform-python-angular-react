import { useState } from 'react';
import { Nav, Card, Table } from 'react-bootstrap';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../shared/api/client';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { LoadingSpinner } from '../../shared/ui/components/LoadingSpinner';
import { EmptyState } from '../../shared/ui/components/EmptyState';
import { QUERY_KEYS } from '../../shared/config/constants';
import type { Canal, Oficina, Ejecutivo } from '../../entities/referencias/model/types';

type Tab = 'canales' | 'oficinas' | 'ejecutivos';

export function ReferenciasPage() {
  const [tab, setTab] = useState<Tab>('canales');

  const { data: canales, isLoading: loadingCanales } = useQuery<Canal[]>({
    queryKey: [QUERY_KEYS.REFERENCIAS_CANALES],
    queryFn: async () => { const { data } = await apiClient.get<Canal[]>('/referencias/canales'); return data; },
    enabled: tab === 'canales',
  });

  const { data: oficinas, isLoading: loadingOficinas } = useQuery<Oficina[]>({
    queryKey: [QUERY_KEYS.REFERENCIAS_OFICINAS],
    queryFn: async () => { const { data } = await apiClient.get<Oficina[]>('/referencias/oficinas'); return data; },
    enabled: tab === 'oficinas',
  });

  const { data: ejecutivos, isLoading: loadingEjecutivos } = useQuery<Ejecutivo[]>({
    queryKey: [QUERY_KEYS.REFERENCIAS_EJECUTIVOS],
    queryFn: async () => { const { data } = await apiClient.get<Ejecutivo[]>('/referencias/ejecutivos'); return data; },
    enabled: tab === 'ejecutivos',
  });

  const isLoading = (tab === 'canales' && loadingCanales) || (tab === 'oficinas' && loadingOficinas) || (tab === 'ejecutivos' && loadingEjecutivos);

  return (
    <div>
      <PageHeader title="Referencias" subtitle="Catálogos del sistema" icon="bi-diagram-3" />

      <Card className="shadow-sm" style={{ border: 'none' }}>
        <Card.Header className="bg-white border-0 pt-3">
          <Nav variant="tabs" activeKey={tab} onSelect={(tabKey) => setTab(tabKey as Tab)}>
            <Nav.Item><Nav.Link eventKey="canales"><i className="bi bi-broadcast me-2" />Canales</Nav.Link></Nav.Item>
            <Nav.Item><Nav.Link eventKey="oficinas"><i className="bi bi-building me-2" />Oficinas</Nav.Link></Nav.Item>
            <Nav.Item><Nav.Link eventKey="ejecutivos"><i className="bi bi-person-badge me-2" />Ejecutivos</Nav.Link></Nav.Item>
          </Nav>
        </Card.Header>
        <Card.Body className="p-0">
          {isLoading ? (
            <LoadingSpinner fullPage />
          ) : (
            <>
              {tab === 'canales' && (
                canales?.length ? (
                  <Table hover className="mb-0">
                    <thead><tr><th>ID</th><th>Nombre</th><th>Código</th></tr></thead>
                    <tbody>{canales.map((canal) => <tr key={canal.id}><td>{canal.id}</td><td>{canal.nombre}</td><td>{canal.codigo ?? '—'}</td></tr>)}</tbody>
                  </Table>
                ) : <EmptyState icon="bi-broadcast" title="Sin canales" />
              )}
              {tab === 'oficinas' && (
                oficinas?.length ? (
                  <Table hover className="mb-0">
                    <thead><tr><th>ID</th><th>Nombre</th><th>Canal</th></tr></thead>
                    <tbody>{oficinas.map((oficina) => <tr key={oficina.id}><td>{oficina.id}</td><td>{oficina.nombre}</td><td>{oficina.canal_id ?? '—'}</td></tr>)}</tbody>
                  </Table>
                ) : <EmptyState icon="bi-building" title="Sin oficinas" />
              )}
              {tab === 'ejecutivos' && (
                ejecutivos?.length ? (
                  <Table hover className="mb-0">
                    <thead><tr><th>Usuario</th><th>Nombre</th><th>Canal</th><th>Oficina</th></tr></thead>
                    <tbody>{ejecutivos.map((ejecutivo) => <tr key={ejecutivo.id}><td className="font-monospace">{ejecutivo.usuario_asesor}</td><td>{ejecutivo.nombre ?? '—'}</td><td>{ejecutivo.canal ?? '—'}</td><td>{ejecutivo.oficina ?? '—'}</td></tr>)}</tbody>
                  </Table>
                ) : <EmptyState icon="bi-person-badge" title="Sin ejecutivos" />
              )}
            </>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}
