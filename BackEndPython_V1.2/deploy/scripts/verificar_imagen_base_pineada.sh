#!/usr/bin/env bash
# AP-0117 -- Guard de CI: verifica que el Dockerfile referencie la imagen base por DIGESTO
# inmutable (sha256) y desde un registry aprobado, no por un tag mutable. Falla el build si
# la base no esta pineada, garantizando procedencia byte-a-byte del software base.
#
# Uso: verificar_imagen_base_pineada.sh <ruta_al_Dockerfile>
# Responsabilidad: equipo de desarrollo (se ejecuta en el pipeline de CI).
set -euo pipefail

DOCKERFILE="${1:-Docker/Dockerfile.backend}"

APROBADOS_REGEX='^(python|mcr.microsoft.com/|[a-z0-9.-]+.azurecr.io/)'

lineas_from="$(grep -iE '^FROM ' "${DOCKERFILE}" || true)"
if [[ -z "${lineas_from}" ]]; then
  echo "AP-0117 ERROR: no se encontro ninguna instruccion FROM en ${DOCKERFILE}"; exit 1
fi

fallo=0
while IFS= read -r linea; do
  ref="$(echo "${linea}" | awk '{print $2}')"
  if [[ "${ref}" != *@sha256:* ]]; then
    echo "AP-0117 FALLO: imagen base sin digesto (usar FROM imagen@sha256:...): ${ref}"
    fallo=1
  fi
  if ! echo "${ref}" | grep -qE "${APROBADOS_REGEX}"; then
    echo "AP-0117 AVISO: registry no reconocido como aprobado: ${ref}"
  fi
done <<< "${lineas_from}"

if [[ "${fallo}" -ne 0 ]]; then
  echo "AP-0117: la imagen base debe estar pineada por digesto. Obtenga el digesto con:"
  echo "  docker buildx imagetools inspect python:3.14-slim"
  exit 1
fi
echo "AP-0117 OK: imagenes base pineadas por digesto y desde registries aprobados."