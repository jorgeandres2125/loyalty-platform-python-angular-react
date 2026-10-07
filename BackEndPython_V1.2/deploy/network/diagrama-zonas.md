# AP-0150 -- Diagrama de zonas y flujos de red (SUFI)

Fuente canonica: [`inventario-segmentacion.yaml`](inventario-segmentacion.yaml). Este diagrama
es la representacion visual; el gate de CI (`validar_segmentacion.py`) valida el inventario, no
el diagrama. Mantener ambos sincronizados.

```mermaid
flowchart TB
    NET([Internet])
    subgraph DMZ["DMZ  ·  WAF + Firewall perimetral + IPS"]
        AGW[Application Gateway / WAF]
    end
    subgraph WEB["Capa Web  (snet-web / sufi-web)"]
        SPA[SPA React + reverse proxy]
    end
    subgraph APP["Capa Aplicacion  (snet-app / sufi-app)"]
        API[FastAPI  ·  mTLS AP-0003  ·  borde AP-0064]
    end
    subgraph DATA["Capa de Datos  (snet-data / sufi-data)"]
        SQL[(SQL Server 2019  ·  Private Endpoint)]
    end
    subgraph SHARED["Servicios Compartidos  (snet-shared)"]
        SVC[KMS/HSM · correo · NTP · monitoreo]
    end
    subgraph MGMT["Red de Gestion  ·  VPN + Bastion + MFA (AP-0052)"]
        BAS[Bastion / Jump server]
    end

    NET -->|443| AGW
    AGW -->|443| SPA
    SPA -->|443 mTLS| API
    API -->|1433| SQL
    API -->|443| SVC
    BAS -.->|22| SPA
    BAS -.->|22| API
    BAS -.->|1433 / 3389| SQL
    BAS -.->|22| SVC

    SQL -. x  bloqueado .-> NET
    SPA -. x  bloqueado .-> SQL
```

## Flujos bloqueados (invariantes verificadas por el gate)

| Origen | Destino | Motivo |
|---|---|---|
| Internet | Capa App / Datos / Compartidos | Ningun componente critico se expone directo a Internet |
| Capa Web | Capa de Datos | La web nunca habla directo con SQL Server |
| Capa de Datos | Internet | SQL sin salida a Internet (egress deny) |

## Correspondencia de artefactos

| Zona | Azure (`network.bicep`) | Kubernetes (`networkpolicies.yaml`) | AWS (`aws-security-groups.tf`) |
|---|---|---|---|
| DMZ | Application Gateway + WAF policy | Ingress controller (`zona: ingress`) | ALB + WAFv2 |
| Web | `snet-web` + `nsg-web` | ns `sufi-web` | `sg-sufi-web` |
| App | `snet-app` + `nsg-app` | ns `sufi-app` | `sg-sufi-app` |
| Datos | `snet-data` + `nsg-data` + Private Endpoint | ns `sufi-data` | `sg-sufi-data` |
| Compartidos | `snet-shared` | ns `zona: shared` | subnet privada compartida |
| Gestion | AzureBastionSubnet + GatewaySubnet | fuera del cluster | Bastion / SSM |
