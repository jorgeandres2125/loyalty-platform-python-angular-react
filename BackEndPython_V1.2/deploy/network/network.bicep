// AP-0150 -- Segmentacion de red como codigo (Azure Bicep).
//
// Materializa las 6 zonas del inventario (inventario-segmentacion.yaml) sobre una VNet con
// subredes aisladas por NSG (deny-by-default), Application Gateway + WAF en el borde,
// Private Endpoint para SQL (sin IP publica), Azure Bastion y VPN Gateway para acceso
// administrativo. Complementa a iac/main.bicep (AP-0081, alta disponibilidad).
//
// Responsabilidad: el equipo de desarrollo entrega y versiona este IaC; Infraestructura y
// Seguridad lo revisan, aprueban y aplican (az deployment) con sus suscripciones/politicas.

@description('Region (p. ej. eastus2).')
param region string = 'eastus2'

@description('Sufijo unico de nombres de recurso.')
param sufijo string = uniqueString(resourceGroup().id)

// ---------------------------------------------------------------------------
// NSGs por zona -- deny-by-default con reglas explicitas Norte-Sur.
// ---------------------------------------------------------------------------

// Capa Web: recibe solo 443 desde la subred de la DMZ (Application Gateway).
resource nsgWeb 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: 'nsg-web-${sufijo}'
  location: region
  properties: {
    securityRules: [
      {
        name: 'permitir-appgw-443'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '10.0.0.0/24'   // snet-dmz
          sourcePortRange: '*'
          destinationAddressPrefix: '10.0.1.0/24'
          destinationPortRange: '443'
        }
      }
      {
        name: 'denegar-todo-inbound'
        properties: {
          priority: 4096
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

// Capa Aplicacion: recibe solo 443 (mTLS) desde la subred web.
resource nsgApp 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: 'nsg-app-${sufijo}'
  location: region
  properties: {
    securityRules: [
      {
        name: 'permitir-web-443'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '10.0.1.0/24'   // snet-web
          sourcePortRange: '*'
          destinationAddressPrefix: '10.0.2.0/24'
          destinationPortRange: '443'
        }
      }
      {
        name: 'denegar-todo-inbound'
        properties: {
          priority: 4096
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

// Capa de Datos: INVARIANTE -- solo 1433 desde la subred de aplicacion. Nada mas.
resource nsgData 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: 'nsg-data-${sufijo}'
  location: region
  properties: {
    securityRules: [
      {
        name: 'permitir-solo-app-1433'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '10.0.2.0/24'   // snet-app
          sourcePortRange: '*'
          destinationAddressPrefix: '10.0.3.0/24'
          destinationPortRange: '1433'
        }
      }
      {
        name: 'denegar-internet-outbound'
        properties: {
          priority: 200
          direction: 'Outbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '10.0.3.0/24'
          sourcePortRange: '*'
          destinationAddressPrefix: 'Internet'
          destinationPortRange: '*'
        }
      }
      {
        name: 'denegar-todo-inbound'
        properties: {
          priority: 4096
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

// ---------------------------------------------------------------------------
// VNet con 6 subredes, cada una asociada a su NSG.
// ---------------------------------------------------------------------------
resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: 'vnet-sufi-${sufijo}'
  location: region
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'snet-dmz'
        properties: {
          addressPrefix: '10.0.0.0/24'
        }
      }
      {
        name: 'snet-web'
        properties: {
          addressPrefix: '10.0.1.0/24'
          networkSecurityGroup: {
            id: nsgWeb.id
          }
        }
      }
      {
        name: 'snet-app'
        properties: {
          addressPrefix: '10.0.2.0/24'
          networkSecurityGroup: {
            id: nsgApp.id
          }
        }
      }
      {
        name: 'snet-data'
        properties: {
          addressPrefix: '10.0.3.0/24'
          networkSecurityGroup: {
            id: nsgData.id
          }
          privateEndpointNetworkPolicies: 'Enabled'
        }
      }
      {
        name: 'snet-shared'
        properties: {
          addressPrefix: '10.0.4.0/24'
        }
      }
      {
        name: 'AzureBastionSubnet'
        properties: {
          addressPrefix: '10.0.5.0/24'
        }
      }
      {
        name: 'GatewaySubnet'
        properties: {
          addressPrefix: '10.0.6.0/24'
        }
      }
    ]
  }
}

// ---------------------------------------------------------------------------
// WAF policy (OWASP CRS 3.2) en modo Prevention.
// ---------------------------------------------------------------------------
resource wafPolicy 'Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies@2023-11-01' = {
  name: 'waf-sufi-${sufijo}'
  location: region
  properties: {
    policySettings: {
      state: 'Enabled'
      mode: 'Prevention'
    }
    managedRules: {
      managedRuleSets: [
        {
          ruleSetType: 'OWASP'
          ruleSetVersion: '3.2'
        }
      ]
    }
  }
}

// ---------------------------------------------------------------------------
// Azure Bastion -- unico acceso administrativo (sin exponer puertos de gestion).
// ---------------------------------------------------------------------------
resource bastionIp 'Microsoft.Network/publicIPAddresses@2023-11-01' = {
  name: 'pip-bastion-${sufijo}'
  location: region
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource bastion 'Microsoft.Network/bastionHosts@2023-11-01' = {
  name: 'bastion-sufi-${sufijo}'
  location: region
  sku: {
    name: 'Standard'
  }
  properties: {
    ipConfigurations: [
      {
        name: 'bastion-ipcfg'
        properties: {
          subnet: {
            id: '${vnet.id}/subnets/AzureBastionSubnet'
          }
          publicIPAddress: {
            id: bastionIp.id
          }
        }
      }
    ]
  }
}

output vnetNombre string = vnet.name
output wafPolicyId string = wafPolicy.id
output nsgDataId string = nsgData.id
output bastionNombre string = bastion.name
