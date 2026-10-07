# Handoff a Infraestructura -- Cierre de AP-0117 (firma del software complementario)

El **lado proyecto** esta completo (control en AMARILLO). Para cerrar a **VERDE**,
Infraestructura y Seguridad deben ejecutar y evidenciar el enforcement de firma a nivel de SO.

## Lo que ya aporta el proyecto (evidencia lista)
- Imagen base oficial con politica de pineo por digesto y guard de CI
  (deploy/scripts/verificar_imagen_base_pineada.sh).
- Driver ODBC de Microsoft instalado desde repo firmado (clave GPG verificada) -- ver Dockerfile.
- Imagen propia firmada con cosign (AP-0149) e inventariada por SBOM (.github/workflows/sbom.yml).
- Politica de admision que solo acepta imagenes firmadas de registries aprobados
  (deploy/policy/admission-image-signature-policy.yaml).
- Inventario, procedimiento de verificacion, RACI y plantilla de atestacion en la carpeta Security.

## Lo que debe ejecutar Infraestructura y Seguridad
1. Habilitar y atestar **Secure Boot** en nodos AKS y VMs (Azure Trusted Launch).
2. Habilitar **enforcement de firma de modulos** en Linux (module.sig_enforce=1) y **HVCI o
   WDAC** en Windows Server; usar solo drivers firmados (WHQL).
3. Definir **fuentes de parcheo autorizadas** (WSUS, Update Manager, repos firmados) y
   registrar la actualizacion de drivers.
4. Aplicar la **politica de admision** (Kyverno) en modo Enforce sobre el cluster.
5. Ejecutar el **procedimiento de verificacion** (Security, Procedimiento_Verificacion_Firmas_AP-0117.md)
   y archivar las salidas.
6. Firmar la **atestacion** (Security, Atestacion_Infraestructura_AP-0117.md).

## Criterio de cierre a VERDE
Atestacion firmada + evidencias de enforcement (Secure Boot, modulos y drivers firmados) +
politica de admision activa + inventario del proyecto. Con eso, AP-0117 pasa de AMARILLO a VERDE.