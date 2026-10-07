# Runbook -- Failover de Alta Disponibilidad (AP-0081)

**Objetivo:** procedimiento reproducible para verificar y ejercitar la tolerancia a fallos
de la capa de aplicacion y de base de datos, sin perdida de servicio.

## Precondiciones
- Cluster AKS multi-zona con el Deployment `sufi-backend` (tres o mas replicas, PDB, anti-afinidad).
- Azure SQL zona-redundante activo.

## A. Prueba de fallo de replica (capa de aplicacion)
1. Listar las replicas y sus zonas: `kubectl get pods -l app=sufi-backend -o wide`.
2. Eliminar una replica: `kubectl delete pod <nombre-pod>`.
3. Verificar que el trafico continua sin errores (las sondas de readiness mantienen el
   balanceo solo hacia replicas sanas) y que Kubernetes recrea la replica.
4. **Evidencia:** salida de `kubectl get pods` antes y despues, y captura del monitoreo sin caida.

## B. Prueba de drain de nodo (mantenimiento voluntario)
1. `kubectl drain <nodo> --ignore-daemonsets --delete-emptydir-data`.
2. El PodDisruptionBudget (minAvailable dos) impide que el drain reduzca la capacidad
   por debajo de 2 replicas disponibles.
3. **Evidencia:** el servicio permanece operativo durante todo el drain.

## C. Failover de base de datos (Azure SQL)
1. Forzar el failover del Failover Group a la replica secundaria (ver Runbook de Restauracion DR).
2. La app tolera el corte transitorio: pool_pre_ping descarta las conexiones muertas y
   la readiness marca 503 momentaneamente hasta que la BD responde de nuevo.
3. **Evidencia:** log de la app reconectando y readiness volviendo a 200.

## Criterio de exito
Servicio ininterrumpido (o interrupcion menor al RTO acordado) en los tres escenarios.