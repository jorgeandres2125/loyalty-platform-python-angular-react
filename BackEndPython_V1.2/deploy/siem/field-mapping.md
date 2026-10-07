# AP-0134 - Mapeo de campos y notas de paging y SOAR

## Campos del evento (logger sufi.seguridad) hacia ECS o Sentinel ASIM

| Campo app | ECS | Sentinel ASIM | Notas |
|---|---|---|---|
| timestamp | @timestamp | TimeGenerated | ms mas timezone (AP-0024) |
| evento_seguridad | event.action | EventType | tipo de evento |
| severidad | event.severity | EventSeverity | baja a critica |
| resultado | event.outcome | EventResult | exito o fallo |
| actor (o usuario) | user.name | ActorUsername | sujeto |
| ip (o ip_publica) | source.ip | SrcIpAddr | origen |
| metodo | http.request.method | HttpRequestMethod | |
| ruta (o recurso) | url.path | Url | |
| evento_id (o correlation_id) | event.id | CorrelationId | traza extremo a extremo |
| detalle | message | AdditionalFields | ya redactado (AP-0087) |

## Notificacion y paging

- **PagerDuty Events API v2**: enrutar severidad critica desde el SIEM (o via SOAR) a un
  Integration Key; escalado on-call con rotacion. La severidad alta va a Teams o Slack mas
  correo (ya cubierto por la app como respaldo). La media va solo a dashboard o digest.
- **Deduplicacion**: usar dedup_key = evento_seguridad mas actor mas ip (misma clave que el
  alertador de la app) para colapsar tormentas en un incidente con contador.

## SOAR (playbook de ejemplo: cuenta bloqueada o fuerza bruta)

1. Trigger: analytics rule Fuerza bruta o Acceso tras bloqueo.
2. Enriquecer: geo y ASN de source.ip, historial del user.name, dispositivos (AP-0014).
3. Contener (opcional, con aprobacion): forzar token_version mas uno del usuario via
   endpoint admin (invalida sus sesiones, AP-0049 y AP-0133) o bloquear la IP en el WAF
   (AP-0064).
4. Notificar: crear incidente mas paging; adjuntar CorrelationId para la traza.
5. Registrar: la accion de respuesta se audita (AP-0028) con el mismo CorrelationId.

## Anti-falsos-positivos

- Watchlist de cuentas de servicio e IPs de health-check y scanners internos (excluir).
- Umbrales por regla parametrizables (no hardcode); revision trimestral (tuning loop).
- KPI de precision = alertas verdaderas sobre el total; objetivo mayor o igual a 0.8 tras
  la estabilizacion.