// The cloud POC sandbox: the same Streamlit app as the local POC, de-identified data baked into the image.
// Its own Container Apps environment and resource group; it gets no database credentials and no file shares.
param location string
param tags object
param token string
@secure()
param demoPassword string
@secure()
param logfireToken string
param hospitalResourceGroup string
param registryLoginServer string
param foundryAccountName string
param foundryEndpoint string
param foundryDeployment string
param pocExists bool

var placeholderImage = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-poc-${token}'
  location: location
  tags: tags
  properties: { sku: { name: 'PerGB2018' }, retentionInDays: 30 }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-poc-${token}'
  location: location
  tags: tags
}

resource foundry 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: foundryAccountName
  scope: resourceGroup(hospitalResourceGroup)
}

resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-poc-${token}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: { customerId: logs.properties.customerId, sharedKey: logs.listKeys().primarySharedKey }
    }
  }
}

module pocImage 'fetch-image.bicep' = {
  name: 'poc-image'
  params: { exists: pocExists, name: 'ca-poc-${token}' }
}

resource poc 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-poc-${token}'
  location: location
  tags: union(tags, { 'azd-service-name': 'poc' })
  identity: { type: 'UserAssigned', userAssignedIdentities: { '${identity.id}': {} } }
  properties: {
    environmentId: env.id
    configuration: {
      ingress: { external: true, targetPort: 8501, transport: 'auto', allowInsecure: false }
      registries: [{ server: registryLoginServer, identity: identity.id }]
      secrets: concat([
        { name: 'poc-password', value: demoPassword }
        { name: 'foundry-key', value: foundry.listKeys().key1 }
      ], empty(logfireToken) ? [] : [{ name: 'logfire-token', value: logfireToken }])
    }
    template: {
      containers: [
        {
          name: 'poc'
          image: pocExists ? pocImage.outputs.image : placeholderImage
          env: concat([
            { name: 'POC_PASSWORD', secretRef: 'poc-password' }
            { name: 'POC_ENV_LABEL', value: 'Azure sandbox (${resourceGroup().name})' }
            { name: 'COPILOT_PROVIDER', value: 'foundry' }
            { name: 'FOUNDRY_ENDPOINT', value: foundryEndpoint }
            { name: 'FOUNDRY_DEPLOYMENT', value: foundryDeployment }
            { name: 'FOUNDRY_API_KEY', secretRef: 'foundry-key' }
          ], empty(logfireToken) ? [] : [{ name: 'LOGFIRE_TOKEN', secretRef: 'logfire-token' }])
          resources: { cpu: json('0.5'), memory: '1Gi' }
        }
      ]
      // one replica: Streamlit keeps session state in memory
      scale: { minReplicas: 1, maxReplicas: 1 }
    }
  }
}

output identityPrincipalId string = identity.properties.principalId
output pocUrl string = 'https://${poc.properties.configuration.ingress.fqdn}'
