# AP-0150 -- Segmentacion de red por controles de seguridad

Este paquete es el **lado del proyecto** del control AP-0150 (separar los componentes de la
solucion a nivel de red mediante Firewalls, WAF, IPS, IDS y microsegmentacion).

El nucleo del control (desplegar WAF, firewalls, IDS/IPS, VPN y bastion) es responsabilidad de
**Infraestructura y Seguridad**. Lo que el proyecto entrega y deja verificable por codigo es la
**segmentacion declarada como codigo**, la **validacion anti-topologia-plana** y los
**controles compensatorios de capa 7** ya implementados.

## Contenido

| Archivo | Que es |
|---|---|
| `inventario-segmentacion.yaml` | Fuente canonica: zonas, flujos permitidos, flujos prohibidos, controles, evidencias. |
| `validar_segmentacion.py` | Gate de CI: falla si la topologia es plana (BD alcanzable fuera de la capa app, componente critico expuesto a Internet, o falta WAF). |
| `networkpolicies.yaml` | Microsegmentacion en Kubernetes/OpenShift (deny-by-default; BD solo desde la capa app por 1433). |
| `network.bicep` | Segmentacion en Azure: VNet + 6 subredes + NSG + WAF policy + Bastion + Private Endpoint. |
| `aws-security-groups.tf` | Equivalencia en AWS: VPC + Security Groups referenciados + WAFv2. |
| `diagrama-zonas.md` | Diagrama de zonas y flujos (mermaid) y tabla de correspondencia de artefactos. |

## Ejecutar el gate localmente

```bash
python deploy/network/validar_segmentacion.py
```

Sale con codigo 0 si la segmentacion es valida; con codigo 1 (y el detalle de cada invariante
violada) si no. Se ejecuta tambien en CI (`.github/workflows/network-segmentation.yml`).

## Invariantes que se garantizan

1. Ninguna zona critica (web, app, datos, compartidos, gestion) recibe trafico directo de Internet.
2. La capa de datos solo es alcanzable desde la capa de aplicacion (y gestion), unicamente por 1433.
3. El ingreso publico entra solo por una zona con WAF (deny-by-default en el borde).
4. Ningun flujo declarado como prohibido aparece entre los permitidos.
5. En Kubernetes existe deny-by-default por namespace y SQL solo acepta ingreso de la capa app.

## Controles compensatorios ya implementados (lado aplicacion)

| Compensatorio | Control |
|---|---|
| mTLS en rutas criticas | AP-0003 |
| Borde de confianza (solo el edge es de confianza) | AP-0064 |
| Red administrativa por CIDR | AP-0052 |
| Minimo privilegio en BD (sin `sa`) | AP-0056 |
| Defaults fail-secure | AP-0109 |
| Rate limiting / WAF-lite de aplicacion | AP-0166, AP-0202, AP-0204 |
| Deteccion (alertador de seguridad, alimenta IDS/SIEM) | AP-0134 |

## Estado del control

**AMARILLO.** El lado del proyecto esta completo y verificado por el gate. El cierre a **Verde**
requiere que Infraestructura y Seguridad desplieguen los controles y aporten las evidencias
E1-E9 listadas en `inventario-segmentacion.yaml` (`evidencias_para_verde`). Ver
`../../../Security/HANDOFF_Infraestructura_AP-0150.md`.
