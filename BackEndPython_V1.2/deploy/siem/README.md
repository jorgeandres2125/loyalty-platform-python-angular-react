# AP-0134 - Pipeline de deteccion y alertamiento de eventos de seguridad (Alternativa C)

Handoff para Infraestructura y DevSecOps. La aplicacion SUFI **ya genera** eventos de
seguridad estructurados (JSON) en el logger sufi.seguridad, clasificados por severidad
(AP-0022, 0023 y 0024), sellados con cadena SHA-256 (AP-0025) y con retencion clasificada
(AP-0026), y **ya emite alertas compensatorias** desde la app (correo AP-0088 o webhook)
para eventos de severidad mayor o igual al umbral (ver ServicioAlertaSeguridad y
AlertaHandler). Estos artefactos conectan ese stream con el pipeline enterprise:
shipping hacia la plataforma de logs, luego SIEM (alertas por consulta), observabilidad
(dashboards) y paging.

## Topologia

```
app (stdout JSON)  ->  Fluent Bit (fluent-bit.conf)  ->  OpenSearch, Splunk o Log Analytics
                                                              |-> SIEM: detection-rules.kql  (alertas por consulta)
                                                              |-> Grafana: grafana-dashboard.json  (dashboards)
                                                              |-> PagerDuty u OpsGenie  (paging critica)
```

## Artefactos

| Archivo | Proposito | Responsable |
|---|---|---|
| fluent-bit.conf | Recolecta el JSON de sufi.seguridad y lo envia al destino | Infra |
| detection-rules.kql | Reglas de correlacion como **alertas por consulta** (Microsoft Sentinel o Log Analytics) | SecOps |
| splunk-savedsearches.conf | Equivalente de las mismas reglas en Splunk (SPL) | SecOps |
| grafana-dashboard.json | **Dashboard** de monitoreo importable en Grafana | Observabilidad |
| field-mapping.md | Mapeo de campos app hacia ECS o ASIM y notas de paging y SOAR | SecOps |

## Estados y canales (reutiliza SeveridadSeguridad de la app)

| Severidad | Nivel | Canal | SLO notificacion |
|---|---|---|---|
| critica | CRITICAL | Paging (PagerDuty) mas SIEM | <= 1 min |
| alta | ERROR | Teams o Slack mas correo mas SIEM | <= 5 min |
| media | WARNING | SIEM (dashboard) mas digest | <= 15 min |
| baja o informativa | INFO | Solo log o SIEM | N/A |

## Checklist de evidencia para pasar AP-0134 a VERDE (Infra y SecOps)

- **E1**: shipping operativo (Fluent Bit hacia la plataforma) con el indice sufi-seguridad.
- **E2**: las reglas de detection-rules.kql activas como analytics rules (alertas por consulta).
- **E3**: paging on-call configurado para severidad critica (PagerDuty u OpsGenie).
- **E4**: grafana-dashboard.json publicado y accesible por el equipo de seguridad.

Con E1 a E4 el control alcanza VERDE pleno. Sin ellos, la app ya provee alertamiento
compensatorio real (Amarillo demostrable). Este pipeline es infraestructura, igual que
las capas SIEM de AP-0025 y AP-0026 y el filtrado de AP-0140.