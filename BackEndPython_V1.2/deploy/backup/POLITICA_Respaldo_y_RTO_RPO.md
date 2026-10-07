# Politica de Respaldo y Acuerdo de RTO y RPO (AP-0081)

> Documento para revision y **firma del negocio**. Las cifras son propuestas del proyecto.

## 1. Politica de respaldo
| Aspecto | Definicion propuesta |
|---|---|
| Frecuencia | Backup completo diario (03:00 UTC) via CronJob cronjob-backup.yaml |
| Cifrado | AES-256 en reposo; clave gestionada por KMS o Key Vault (AP-0180) |
| Destino fuera de sitio | Azure Storage geo-redundante (GRS o RA-GRS) en region distinta a la primaria |
| Inmutabilidad | Blob inmutable (WORM) recomendado, para resistir borrado y ransomware |
| Retencion | 30 dias operativa; retencion regulatoria segun AP-0026 |
| Verificacion | Checksum sha256 en cada backup; prueba de restauracion periodica (trimestral minimo) |
| Responsable de ejecucion | Automatizado (CronJob); supervision de Infraestructura |

## 2. Acuerdo de RTO y RPO (propuesto)
| Escenario | RPO objetivo | RTO objetivo |
|---|---|---|
| Fallo de replica o nodo (HA) | 0 (sin perdida) | Segundos (automatico) |
| Failover de BD intra-region (zona) | 0 (replica sincrona) | Minutos (automatico) |
| Desastre regional -- geo-replica (Failover Group) | menor o igual a 5 minutos | menor o igual a 4 horas (warm standby) |
| Restauracion desde respaldo fuera de sitio | menor o igual a 24 horas | menor o igual a 8 horas |

## 3. Firmas
| Rol | Nombre | Firma | Fecha |
|---|---|---|---|
| Dueno del negocio | | | |
| Responsable de Infraestructura | | | |
| Responsable de Seguridad | | | |