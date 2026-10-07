# Handoff a Infraestructura y Seguridad -- Cierre de AP-0120 (File Integrity Monitoring)

El **lado proyecto** esta completo (control en AMARILLO). Para cerrar a **VERDE**,
Infraestructura y Seguridad deben implementar y evidenciar el FIM de los archivos del SO.

## Lo que ya aporta el proyecto (evidencia lista)
- Contenedor endurecido: readOnlyRootFilesystem, sin escalada de privilegios, capabilities drop
  ALL, rutas escribibles solo en emptyDir (deployment.yaml) -- el codigo no cambia en runtime.
- Baseline de integridad de la app generado en CI (deploy/scripts/generar_baseline_integridad.py).
- Self-check al arranque (VerificadorIntegridadArchivos mas ServicioVerificacionIntegridad) que
  reporta el resultado en la bitacora de seguridad sufi.seguridad, con severidad (AP-0023), cadena
  tamper-evident (AP-0025) y retencion (AP-0026).
- Imagen firmada (AP-0149) y admision de imagenes firmadas (AP-0117): integridad por construccion.
- Inventario de archivos criticos, procedimiento FIM con runbook y RACI en Security.

## Lo que deben ejecutar Infraestructura y Seguridad
1. Habilitar **Microsoft Defender for Servers (FIM)** en todos los nodos y VMs con el baseline del SO
   (o desplegar Wazuh/AIDE como alternativa open source).
2. Conectar a **Microsoft Sentinel** o **Defender for Cloud**: reglas de alerta al SOC y
   almacenamiento inmutable (WORM) con la retencion definida.
3. Ejecutar una **prueba de deteccion (fire-drill)** y documentarla.
4. Firmar la **atestacion** (Security, Atestacion_Infraestructura_FIM_AP-0120.md).

## Criterio de cierre a VERDE
Atestacion firmada + Defender for Servers FIM activo + evidencia de deteccion, alerta y retencion
inmutable + el aporte del proyecto. Con eso, AP-0120 pasa de AMARILLO a VERDE.