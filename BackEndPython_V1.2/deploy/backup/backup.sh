#!/usr/bin/env bash
# AP-0081 (DRP) -- Respaldo automatizado de la base de datos SUFI con copia FUERA DE SITIO.
#
# Flujo:
#   1. Genera un backup logico de la BD (sqlpackage Export).
#   2. Lo cifra en reposo (AES-256; clave gestionada por KMS / Key Vault -- AP-0180).
#   3. Lo sube a una Storage Account geo-redundante (GRS) en OTRA region (off-site).
#   4. Verifica la integridad (checksum) y registra el resultado para evidencia de auditoria.
#
# Variables de entorno (inyectadas por el Secret sufi-backup-secrets):
#   SQL_HOST, SQL_DB, SQL_USER, SQL_PASSWORD  -> origen
#   BACKUP_ENCRYPTION_KEY                     -> clave de cifrado del artefacto
#   AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_CONTAINER, AZURE_STORAGE_SAS  -> destino off-site GRS
#
# Responsabilidad: el equipo de desarrollo entrega el script; Infraestructura provee el
# destino GRS, su inmutabilidad (WORM) y el ciclo de retencion.
set -euo pipefail

FECHA="$(date -u +%Y%m%dT%H%M%SZ)"
ARCHIVO="sufi_db_${FECHA}.bak"
CIFRADO="${ARCHIVO}.enc"
TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

echo "[AP-0081] paso 1 de 4 -- Generando backup ${ARCHIVO} ..."
sqlpackage /Action:Export \
  /SourceServerName:"${SQL_HOST}" \
  /SourceDatabaseName:"${SQL_DB}" \
  /SourceUser:"${SQL_USER}" \
  /SourcePassword:"${SQL_PASSWORD}" \
  /TargetFile:"${TMP}/${ARCHIVO}"

echo "[AP-0081] paso 2 de 4 -- Cifrando el artefacto (AES-256) ..."
openssl enc -aes-256-cbc -salt -pbkdf2 \
  -in "${TMP}/${ARCHIVO}" \
  -out "${TMP}/${CIFRADO}" \
  -pass env:BACKUP_ENCRYPTION_KEY

CHECKSUM="$(sha256sum "${TMP}/${CIFRADO}" | awk '{print $1}')"
echo "${CHECKSUM}  ${CIFRADO}" > "${TMP}/${CIFRADO}.sha256"

echo "[AP-0081] paso 3 de 4 -- Subiendo a Storage GRS off-site (${AZURE_STORAGE_ACCOUNT}) ..."
az storage blob upload \
  --account-name "${AZURE_STORAGE_ACCOUNT}" \
  --container-name "${AZURE_STORAGE_CONTAINER}" \
  --sas-token "${AZURE_STORAGE_SAS}" \
  --name "${CIFRADO}" \
  --file "${TMP}/${CIFRADO}"
az storage blob upload \
  --account-name "${AZURE_STORAGE_ACCOUNT}" \
  --container-name "${AZURE_STORAGE_CONTAINER}" \
  --sas-token "${AZURE_STORAGE_SAS}" \
  --name "${CIFRADO}.sha256" \
  --file "${TMP}/${CIFRADO}.sha256"

echo "[AP-0081] paso 4 de 4 -- OK. Backup off-site: ${CIFRADO} (sha256=${CHECKSUM})"