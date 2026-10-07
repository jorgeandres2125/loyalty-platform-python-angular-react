# Handoff a Infraestructura -- Cierre de AP-0081 (Alta Disponibilidad y DRP)

El **lado proyecto** esta completo (control en AMARILLO). Este documento lista, en orden, lo
que Infraestructura y el negocio deben ejecutar para cerrar el control a **VERDE**. Todos los
artefactos referenciados estan versionados en `BackEndPython_V1.2/deploy`.

## 0. Prerrequisitos
- Suscripcion de Azure y dos regiones (primaria y secundaria).
- Permisos para crear AKS, Azure SQL y Storage.
- Imagen del backend firmada y publicada (workflow `build-sign-release.yml`, AP-0149).

## 1. Provisionar la infraestructura (IaC)
```
az group create --name rg-sufi-prod --location eastus2
az deployment group create /
  --resource-group rg-sufi-prod /
  --template-file deploy/iac/main.bicep /
  --parameters regionPrimaria=eastus2 regionSecundaria=centralus /
               sqlAdminUsuario=<usuario> sqlAdminPassword=<secreto>
```
Esto crea: AKS multi-zona, Azure SQL zona-redundante (Business Critical), Failover Group a la
region secundaria y Storage Account GRS para el respaldo fuera de sitio.

## 2. Crear los Secrets de Kubernetes
- `sufi-backend-secrets`: variables de entorno del backend (cadena de Azure SQL apuntando al
  **endpoint del Failover Group**, JWT, claves de cifrado, `REDIS_URL`, etc.).
- `sufi-backup-secrets`: cadena de BD y credenciales de la Storage Account GRS para el CronJob.
- Recomendado: inyectar via Azure Key Vault (CSI driver), no como Secret plano.

## 3. Redis para alta disponibilidad multi-replica
La app soporta un almacen efimero compartido (OTP, OOB, throttle) via `REDIS_URL`. Provisionar
Azure Cache for Redis y fijar `REDIS_URL=redis://<host>:6379/0` en `sufi-backend-secrets`.
Sin esta URL la app usa memoria de proceso (no comparte estado entre replicas).

## 4. Desplegar el backend (HA)
Ejecutar el workflow `deploy.yml` con `region = primaria` y el `tag` de la imagen firmada.
Aplica el Job de migraciones y hace rolling update sin corte. Verificar:
```
kubectl get pods -l app=sufi-backend -o wide      # replicas en zonas distintas
kubectl get pdb sufi-backend-pdb
```

## 5. Ejecutar y documentar los ensayos (evidencia para el auditor)
1. **Failover HA:** seguir `deploy/backup/RUNBOOK_Failover_HA.md`; registrar en el monitoreo.
2. **Prueba de restauracion:** ejecutar `deploy/backup/restore.sh` y rellenar
   `deploy/backup/ACTA_Prueba_Restauracion.md` (RTO medido, integridad, RPO real).
3. **Simulacro DR:** seguir `deploy/backup/RUNBOOK_Restauracion_DR.md` (failover del grupo +
   despliegue en region secundaria con `deploy.yml region=secundaria`) y rellenar
   `deploy/backup/ACTA_Simulacro_DR.md`.

## 6. Aprobacion del negocio
Revisar y firmar `deploy/backup/POLITICA_Respaldo_y_RTO_RPO.md` (RTO y RPO acordados).

## 7. Criterio de cierre a VERDE
Topologia desplegada (pasos 1-4) + tres actas firmadas (paso 5) + acuerdo RTO/RPO firmado
(paso 6). Con eso, AP-0081 pasa de AMARILLO a VERDE en la matriz de cumplimiento.

## Matriz de responsabilidad (resumen)
| Paso | Responsable |
|---|---|
| 1 IaC | Infraestructura (revisa el Bicep del proyecto) |
| 2 Secrets | Infraestructura + Seguridad |
| 3 Redis | Infraestructura |
| 4 Despliegue | Desarrollo + Infraestructura |
| 5 Ensayos | Infraestructura + Desarrollo + QA |
| 6 RTO/RPO | Negocio |