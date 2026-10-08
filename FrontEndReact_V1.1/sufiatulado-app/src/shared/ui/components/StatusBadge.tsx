interface Props {
  active: boolean;
  labels?: [string, string];
}

export function StatusBadge({ active, labels = ['Activo', 'Inactivo'] }: Props) {
  return (
    <span
      className={`badge badge-role ${active ? 'bg-success bg-opacity-15 text-success' : 'bg-secondary bg-opacity-15 text-secondary'}`}
    >
      <i className="bi bi-circle-fill me-1 status-dot" />
      {active ? labels[0] : labels[1]}
    </span>
  );
}
