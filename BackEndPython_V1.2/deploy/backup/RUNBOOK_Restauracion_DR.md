# Runbook -- Restauracion ante Desastre (DRP, AP-0081)

**Objetivo:** recuperar la plataforma en la region secundaria tras la perdida de la region
primaria, o restaurar la base de datos desde el respaldo fuera de sitio.

## Criterios de activacion
- Indisponibilidad total y prolongada de la region primaria, o
- Corrupcion logica o evento de ransomware que invalida la base primaria y su replica.

## Roles
- **Coordinador de DR:** decide la activacion y comunica. (Infraestructura)
- **Operador de plataforma:** ejecuta el failover y el despliegue. (Infraestructura y Desarrollo)
- **Verificador:** valida integridad y servicio. (Desarrollo y QA)

## Secuencia
1. **Datos -- failover del Failover Group** a la region secundaria:
   `az sql failover-group set-primary --name <fog> --resource-group <rg> --server <sql-secundario>`.
2. **Computo -- reconstruir y desplegar** en la region secundaria: ejecutar el workflow
   `deploy.yml` con input region igual a secundaria y el tag de imagen firmada vigente.
   (Si el cluster secundario no existe: aplicar el IaC `main.bicep` con regionPrimaria
   apuntando a la region secundaria.)
3. **DNS y borde:** repuntar el trafico (Front Door o DNS) al endpoint secundario.
4. **Verificacion:** la sonda de readiness (ruta health ready) debe responder 200; validar
   login y una transaccion de lectura y escritura.

## Restauracion puntual desde el respaldo fuera de sitio (alternativa o complemento)
1. Ejecutar `restore.sh` con BLOB_NOMBRE igual al artefacto .enc y SQL_TARGET_DB igual a la
   base de verificacion.
2. El script descarga, verifica el sha256, descifra, importa y **mide el RTO real**.
3. Consignar el RTO medido y la ultima transaccion recuperada (RPO real) en el acta.

## Cierre
Registrar tiempos, incidencias y lecciones aprendidas en el Acta de Simulacro de Recuperacion.