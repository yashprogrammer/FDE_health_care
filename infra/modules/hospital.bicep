// The "hospital": MediTrack (legacy) + Discharge Copilot + gateway sharing one Container Apps environment,
// MediTrack's PostgreSQL database, its file shares, and the Azure AI Foundry model deployment.
param location string
param tags object
param token string
@secure()
param pgAdminPassword string
@secure()
param demoPassword string
@secure()
param logfireToken string
param clientIp string
param foundryLocation string
param foundryModelName string
param foundryModelFormat string
param foundryModelVersion string
param foundrySkuName string
param foundryCapacity int
param meditrackExists bool
param copilotExists bool
param gatewayExists bool

var placeholderImage = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
var pgAdminUser = 'citycareadmin'
// application logins are derived from the admin password (letters + digits, so no escaping needed in URLs)
var meditrackDbPassword = 'Md${uniqueString(pgAdminPassword, 'meditrack')}'
var copilotDbPassword = 'Cp${uniqueString(pgAdminPassword, 'copilot_svc')}'
var misDbPassword = 'Mr${uniqueString(pgAdminPassword, 'mis_report')}'

// libpq connection string; password quoted so any admin password works
func conninfo(host string, user string, password string) string =>
  'host=${host} port=5432 dbname=citycare user=${user} password=\'${replace(replace(password, '\\', '\\\\'), '\'', '\\\'')}\' sslmode=require'

// ------------------------------------------------------------------ shared plumbing
resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-hospital-${token}'
  location: location
  tags: tags
  properties: { sku: { name: 'PerGB2018' }, retentionInDays: 30 }
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: 'crcitycare${token}'
  location: location
  tags: tags
  sku: { name: 'Basic' }
  properties: { adminUserEnabled: false }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-hospital-${token}'
  location: location
  tags: tags
}

module acrPull 'acr-pull.bicep' = {
  name: 'hospital-acr-pull'
  params: { registryName: registry.name, principalId: identity.properties.principalId }
}

// ------------------------------------------------------------------ MediTrack's database (stands in for Oracle)
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: 'psql-meditrack-${token}'
  location: location
  tags: tags
  sku: { name: 'Standard_B1ms', tier: 'Burstable' }
  properties: {
    version: '16'
    administratorLogin: pgAdminUser
    administratorLoginPassword: pgAdminPassword
    storage: { storageSizeGB: 32, autoGrow: 'Disabled' }
    backup: { backupRetentionDays: 7, geoRedundantBackup: 'Disabled' }
    highAvailability: { mode: 'Disabled' }
    network: { publicNetworkAccess: 'Enabled' }
    authConfig: { activeDirectoryAuth: 'Disabled', passwordAuth: 'Enabled' }
  }

  resource db 'databases' = {
    name: 'citycare'
    properties: { charset: 'UTF8', collation: 'en_US.utf8' }
  }

  // Container Apps (consumption) egress IPs are not fixed: allow Azure services; logins are password-protected
  resource azure 'firewallRules' = {
    name: 'AllowAzureServices'
    properties: { startIpAddress: '0.0.0.0', endIpAddress: '0.0.0.0' }
  }
}

resource clientRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = if (!empty(clientIp)) {
  parent: postgres
  name: 'ClientIp'
  properties: { startIpAddress: clientIp, endIpAddress: clientIp }
}

var pgHost = postgres.properties.fullyQualifiedDomainName

// ------------------------------------------------------------------ file shares (the hospital's SMB shares)
resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stcitycare${token}'
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: { minimumTlsVersion: 'TLS1_2', allowBlobPublicAccess: false, allowSharedKeyAccess: true }

  resource files 'fileServices' = {
    name: 'default'

    resource documents 'shares' = {
      name: 'documents'
      properties: { shareQuota: 5 }
    }

    resource hotfolder 'shares' = {
      name: 'import-hotfolder'
      properties: { shareQuota: 5 }
    }
  }
}

// ------------------------------------------------------------------ Azure AI Foundry: gpt-oss-20b
resource foundry 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: 'ai-citycare-${token}'
  location: foundryLocation
  tags: tags
  kind: 'AIServices'
  sku: { name: 'S0' }
  properties: {
    customSubDomainName: 'ai-citycare-${token}'
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
}

resource model 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: foundryModelName
  sku: { name: foundrySkuName, capacity: foundryCapacity }
  properties: {
    model: { format: foundryModelFormat, name: foundryModelName, version: foundryModelVersion }
  }
}

var foundryEndpoint = 'https://${foundry.properties.customSubDomainName}.openai.azure.com/openai/v1/'

// ------------------------------------------------------------------ the shared Container Apps environment
resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-hospital-${token}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: { customerId: logs.properties.customerId, sharedKey: logs.listKeys().primarySharedKey }
    }
  }

  resource documentsStorage 'storages' = {
    name: 'documents'
    properties: {
      azureFile: {
        accountName: storage.name
        accountKey: storage.listKeys().keys[0].value
        shareName: storage::files::documents.name
        accessMode: 'ReadWrite'
      }
    }
  }

  resource hotfolderStorage 'storages' = {
    name: 'import-hotfolder'
    properties: {
      azureFile: {
        accountName: storage.name
        accountKey: storage.listKeys().keys[0].value
        shareName: storage::files::hotfolder.name
        accessMode: 'ReadWrite'
      }
    }
  }
}

var registries = [{ server: registry.properties.loginServer, identity: identity.id }]
var identityBlock = { type: 'UserAssigned', userAssignedIdentities: { '${identity.id}': {} } }
var documentsVolume = { name: 'documents', storageType: 'AzureFile', storageName: env::documentsStorage.name }
var hotfolderVolume = { name: 'import-hotfolder', storageType: 'AzureFile', storageName: env::hotfolderStorage.name }
var documentsMount = { volumeName: 'documents', mountPath: '/mnt/documents' }
var hotfolderMount = { volumeName: 'import-hotfolder', mountPath: '/mnt/import_hotfolder' }
var logfireSecret = empty(logfireToken) ? [] : [{ name: 'logfire-token', value: logfireToken }]
var logfireEnv = empty(logfireToken) ? [] : [{ name: 'LOGFIRE_TOKEN', secretRef: 'logfire-token' }]

module meditrackImage 'fetch-image.bicep' = {
  name: 'meditrack-image'
  params: { exists: meditrackExists, name: 'ca-meditrack-${token}' }
}

module copilotImage 'fetch-image.bicep' = {
  name: 'copilot-image'
  params: { exists: copilotExists, name: 'ca-copilot-${token}' }
}

module gatewayImage 'fetch-image.bicep' = {
  name: 'gateway-image'
  params: { exists: gatewayExists, name: 'ca-gateway-${token}' }
}

// ------------------------------------------------------------------ MediTrack HMS (internal only)
resource meditrack 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-meditrack-${token}'
  location: location
  tags: union(tags, { 'azd-service-name': 'meditrack' })
  identity: identityBlock
  dependsOn: [acrPull]
  properties: {
    environmentId: env.id
    configuration: {
      ingress: { external: false, targetPort: 8001, transport: 'http', allowInsecure: true }
      registries: registries
      secrets: [{ name: 'db-url', value: conninfo(pgHost, 'meditrack', meditrackDbPassword) }]
    }
    template: {
      containers: [
        {
          name: 'meditrack'
          image: meditrackExists ? meditrackImage.outputs.image : placeholderImage
          env: [
            { name: 'APP_ROLE', value: 'meditrack' }
            { name: 'MEDITRACK_DB_URL', secretRef: 'db-url' }
          ]
          resources: { cpu: json('0.5'), memory: '1Gi' }
          volumeMounts: [documentsMount, hotfolderMount]
        }
      ]
      // one replica: the hot-folder importer is a background thread
      scale: { minReplicas: 1, maxReplicas: 1 }
      volumes: [documentsVolume, hotfolderVolume]
    }
  }
}

// ------------------------------------------------------------------ Discharge Copilot (internal only)
resource copilot 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-copilot-${token}'
  location: location
  tags: union(tags, { 'azd-service-name': 'copilot' })
  identity: identityBlock
  dependsOn: [acrPull]
  properties: {
    environmentId: env.id
    configuration: {
      ingress: { external: false, targetPort: 8002, transport: 'http', allowInsecure: true }
      registries: registries
      secrets: concat([
        { name: 'db-url', value: conninfo(pgHost, 'copilot_svc', copilotDbPassword) }
        { name: 'foundry-key', value: foundry.listKeys().key1 }
      ], logfireSecret)
    }
    template: {
      containers: [
        {
          name: 'copilot'
          image: copilotExists ? copilotImage.outputs.image : placeholderImage
          env: concat([
            { name: 'APP_ROLE', value: 'copilot' }
            { name: 'COPILOT_DB_URL', secretRef: 'db-url' }
            { name: 'COPILOT_PROVIDER', value: 'foundry' }
            { name: 'FOUNDRY_ENDPOINT', value: foundryEndpoint }
            { name: 'FOUNDRY_DEPLOYMENT', value: model.name }
            { name: 'FOUNDRY_API_KEY', secretRef: 'foundry-key' }
          ], logfireEnv)
          resources: { cpu: json('0.5'), memory: '1Gi' }
          volumeMounts: [hotfolderMount]   // write-back only: no access to patient documents
        }
      ]
      // one replica: the adapter is a background polling thread
      scale: { minReplicas: 1, maxReplicas: 1 }
      volumes: [hotfolderVolume]
    }
  }
}

// ------------------------------------------------------------------ gateway: the only public endpoint
resource gateway 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-gateway-${token}'
  location: location
  tags: union(tags, { 'azd-service-name': 'gateway' })
  identity: identityBlock
  dependsOn: [acrPull]
  properties: {
    environmentId: env.id
    configuration: {
      ingress: { external: true, targetPort: 80, transport: 'auto', allowInsecure: false }
      registries: registries
      secrets: [{ name: 'demo-password', value: demoPassword }]
    }
    template: {
      containers: [
        {
          name: 'gateway'
          image: gatewayExists ? gatewayImage.outputs.image : placeholderImage
          env: [
            { name: 'MEDITRACK_UPSTREAM', value: 'http://${meditrack.name}' }
            { name: 'COPILOT_UPSTREAM', value: 'http://${copilot.name}' }
            { name: 'DEMO_PASSWORD', secretRef: 'demo-password' }
          ]
          resources: { cpu: json('0.25'), memory: '0.5Gi' }
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 1 }
    }
  }
}

// ------------------------------------------------------------------ reset job: IT's DB setup + reseed + clear drafts
resource resetJob 'Microsoft.App/jobs@2024-03-01' = {
  name: 'job-reset-${token}'
  location: location
  tags: tags
  identity: identityBlock
  dependsOn: [acrPull]
  properties: {
    environmentId: env.id
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: 900
      replicaRetryLimit: 0
      manualTriggerConfig: { parallelism: 1, replicaCompletionCount: 1 }
      registries: registries
      secrets: [
        { name: 'admin-url', value: conninfo(pgHost, pgAdminUser, pgAdminPassword) }
        { name: 'meditrack-url', value: conninfo(pgHost, 'meditrack', meditrackDbPassword) }
        { name: 'copilot-url', value: conninfo(pgHost, 'copilot_svc', copilotDbPassword) }
        #disable-next-line use-secure-value-for-secure-inputs // derived from the secure admin password
        { name: 'meditrack-password', value: meditrackDbPassword }
        #disable-next-line use-secure-value-for-secure-inputs // derived from the secure admin password
        { name: 'copilot-password', value: copilotDbPassword }
        #disable-next-line use-secure-value-for-secure-inputs // derived from the secure admin password
        { name: 'mis-password', value: misDbPassword }
      ]
    }
    template: {
      containers: [
        {
          name: 'reset'
          // the postdeploy hook points the job at the freshly deployed app image
          image: meditrackExists ? meditrackImage.outputs.image : placeholderImage
          env: [
            { name: 'APP_ROLE', value: 'reset' }
            { name: 'DB_ADMIN_URL', secretRef: 'admin-url' }
            { name: 'MEDITRACK_DB_URL', secretRef: 'meditrack-url' }
            { name: 'COPILOT_DB_URL', secretRef: 'copilot-url' }
            { name: 'MEDITRACK_DB_PASSWORD', secretRef: 'meditrack-password' }
            { name: 'COPILOT_DB_PASSWORD', secretRef: 'copilot-password' }
            { name: 'MIS_DB_PASSWORD', secretRef: 'mis-password' }
          ]
          resources: { cpu: json('0.5'), memory: '1Gi' }
          volumeMounts: [documentsMount, hotfolderMount]
        }
      ]
      volumes: [documentsVolume, hotfolderVolume]
    }
  }
}

output registryName string = registry.name
output registryLoginServer string = registry.properties.loginServer
output gatewayUrl string = 'https://${gateway.properties.configuration.ingress.fqdn}'
output resetJobName string = resetJob.name
output postgresHost string = pgHost
output foundryAccountName string = foundry.name
output foundryEndpoint string = foundryEndpoint
output foundryDeployment string = model.name
