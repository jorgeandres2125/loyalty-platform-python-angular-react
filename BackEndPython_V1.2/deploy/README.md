# deploy/ -- Alta Disponibilidad y DRP (AP-0081)

Artefactos de despliegue que hacen la plataforma SUFI apta para alta disponibilidad y
recuperacion ante desastres. **Lado proyecto** del control AP-0081 (ver
`Security/Diseno_Alta_Disponibilidad_DRP_AP-0081_SUFI.docx`).

## Estructura
- `k8s/` -- manifiestos Kubernetes:
  - `deployment.yaml` (replicas, anti-afinidad por zona, sondas liveness y readiness, recursos)
  - `pdb.yaml` (PodDisruptionBudget), `hpa.yaml` (autoescalado), `service.yaml`
  - `job-migrations.yaml` (migraciones desacopladas del arranque)
  - `cronjob-backup.yaml` (respaldo diario fuera de sitio)
- `iac/main.bicep` -- AKS multi-zona, Azure SQL zona y geo-redundante (Failover Group),
  Storage geo-redundante (GRS) para el respaldo fuera de sitio.
- `backup/` -- `backup.sh`, `restore.sh`, runbooks y plantillas de acta, politica de respaldo.

## Responsabilidad
- **Desarrollo:** entrega y versiona estos manifiestos, IaC y scripts; provee las sondas de
  salud en la aplicacion.
- **Infraestructura:** aplica el IaC, provisiona el cluster y la BD redundante, ejecuta el
  simulacro de recuperacion.
- **Negocio:** aprueba RTO y RPO.

## Estado
Fase 1 (lado proyecto) completada -> control **AMARILLO**. Cierre a **VERDE** pendiente del
despliegue de la topologia y de los ensayos de HA y de recuperacion (ver plan de cierre en
el documento de diseno).