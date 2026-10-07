// AP-0081 -- Infraestructura como codigo (Azure Bicep) para Alta Disponibilidad y DRP.
// Provisiona de forma declarativa y repetible: AKS multi-zona, Azure SQL zona-redundante
// con geo-replicacion (Failover Group) y Storage Account geo-redundante (GRS) para el
// respaldo fuera de sitio. Parametrizado por region para recrear el entorno en la
// region secundaria durante un desastre.
//
// Responsabilidad: el equipo de desarrollo entrega y versiona este IaC; Infraestructura
// lo revisa, aprueba y aplica (az deployment) con sus suscripciones y politicas.

@description('Region primaria (p. ej. eastus2).')
param regionPrimaria string = 'eastus2'

@description('Region secundaria para DRP (p. ej. centralus).')
param regionSecundaria string = 'centralus'

@description('Sufijo unico de nombres de recurso.')
param sufijo string = uniqueString(resourceGroup().id)

@description('Administrador de Azure SQL (usuario).')
param sqlAdminUsuario string

@secure()
@description('Contrasena del administrador de Azure SQL.')
param sqlAdminPassword string

// ---------------------------------------------------------------------------
// AKS multi-zona: nodos repartidos en 3 zonas de disponibilidad -> HA de computo.
// ---------------------------------------------------------------------------
resource aks 'Microsoft.ContainerService/managedClusters@2024-02-01' = {
  name: 'aks-sufi-${sufijo}'
  location: regionPrimaria
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    dnsPrefix: 'sufi-${sufijo}'
    agentPoolProfiles: [
      {
        name: 'sistema'
        mode: 'System'
        count: 3
        vmSize: 'Standard_D2s_v5'
        availabilityZones: [
          '1'
          '2'
          '3'
        ]
        type: 'VirtualMachineScaleSets'
      }
    ]
  }
}

// ---------------------------------------------------------------------------
// Azure SQL zona-redundante (HA intra-region con failover transparente).
// ---------------------------------------------------------------------------
resource sqlServerPrimario 'Microsoft.Sql/servers@2023-05-01-preview' = {
  name: 'sql-sufi-${sufijo}'
  location: regionPrimaria
  properties: {
    administratorLogin: sqlAdminUsuario
    administratorLoginPassword: sqlAdminPassword
    minimalTlsVersion: '1.2'
  }
}

resource sqlDb 'Microsoft.Sql/servers/databases@2023-05-01-preview' = {
  parent: sqlServerPrimario
  name: 'sufi_db'
  location: regionPrimaria
  sku: {
    name: 'BC_Gen5_2'   // Business Critical -> replicas locales + zona-redundante
    tier: 'BusinessCritical'
  }
  properties: {
    zoneRedundant: true
  }
}

// Servidor secundario para el Failover Group (geo-replicacion a otra region -> DRP).
resource sqlServerSecundario 'Microsoft.Sql/servers@2023-05-01-preview' = {
  name: 'sql-sufi-dr-${sufijo}'
  location: regionSecundaria
  properties: {
    administratorLogin: sqlAdminUsuario
    administratorLoginPassword: sqlAdminPassword
    minimalTlsVersion: '1.2'
  }
}

resource failoverGroup 'Microsoft.Sql/servers/failoverGroups@2023-05-01-preview' = {
  parent: sqlServerPrimario
  name: 'fog-sufi-${sufijo}'
  properties: {
    readWriteEndpoint: {
      failoverPolicy: 'Automatic'
      failoverWithDataLossGracePeriodMinutes: 60
    }
    partnerServers: [
      {
        id: sqlServerSecundario.id
      }
    ]
    databases: [
      sqlDb.id
    ]
  }
}

// ---------------------------------------------------------------------------
// Storage geo-redundante (GRS) para el respaldo FUERA DE SITIO (DRP).
// ---------------------------------------------------------------------------
resource storageBackup 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stsufibkp${sufijo}'
  location: regionPrimaria
  sku: {
    name: 'Standard_RAGRS'   // replica leible en la region secundaria
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

output aksNombre string = aks.name
output failoverGroupEndpoint string = '${failoverGroup.name}.database.windows.net'
output storageBackupNombre string = storageBackup.name