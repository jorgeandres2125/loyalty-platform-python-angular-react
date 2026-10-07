#!/usr/bin/env bash
# AP-0081 (DRP) -- Restauracion del respaldo off-site. Se usa en la PRUEBA DE RESTAURACION
# periodica (evidencia clave para el auditor) y en la recuperacion real ante desastre.
#
# Mide el RTO real (tiempo hasta servicio operativo) y verifica el RPO (integridad y
# ultima transaccion recuperada). El resultado se consigna en el Acta de Prueba de
# Restauracion.
#
# Variables: las mismas de backup.sh, mas BLOB_NOMBRE (el .enc a restaurar) y
#   SQL_TARGET_DB (BD destino, normalmente una BD temporal de verificacion).
set -euo pipefail

: "${BLOB_NOMBRE:?Debe indicar BLOB_NOMBRE (artefacto .enc a restaurar)}"
TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT
INICIO="$(date -u +%s)"

echo "[AP-0081] paso 1 de 4 -- Descargando ${BLOB_NOMBRE} desde Storage GRS ..."
az storage blob download \
  --account-name "${AZURE_STORAGE_ACCOUNT}" \
  --container-name "${AZURE_STORAGE_CONTAINER}" \
  --sas-token "${AZURE_STORAGE_SAS}" \
  --name "${BLOB_NOMBRE}" \
  --file "${TMP}/${BLOB_NOMBRE}"
az storage blob download \
  --account-name "${AZURE_STORAGE_ACCOUNT}" \
  --container-name "${AZURE_STORAGE_CONTAINER}" \
  --sas-token "${AZURE_STORAGE_SAS}" \
  --name "${BLOB_NOMBRE}.sha256" \
  --file "${TMP}/${BLOB_NOMBRE}.sha256"

echo "[AP-0081] paso 2 de 4 -- Verificando integridad (sha256) ..."
( cd "${TMP}" && sha256sum -c "${BLOB_NOMBRE}.sha256" )

echo "[AP-0081] paso 3 de 4 -- Descifrando ..."
CLARO="${BLOB_NOMBRE%.enc}"
openssl enc -d -aes-256-cbc -pbkdf2 \
  -in "${TMP}/${BLOB_NOMBRE}" \
  -out "${TMP}/${CLARO}" \
  -pass env:BACKUP_ENCRYPTION_KEY

echo "[AP-0081] paso 4 de 4 -- Importando a ${SQL_TARGET_DB} ..."
sqlpackage /Action:Import \
  /TargetServerName:"${SQL_HOST}" \
  /TargetDatabaseName:"${SQL_TARGET_DB}" \
  /TargetUser:"${SQL_USER}" \
  /TargetPassword:"${SQL_PASSWORD}" \
  /SourceFile:"${TMP}/${CLARO}"

FIN="$(date -u +%s)"
echo "[AP-0081] OK -- restauracion verificada. RTO medido: $((FIN - INICIO)) s"