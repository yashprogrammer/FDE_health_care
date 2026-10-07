// CityCare Discharge Copilot - Azure deployment (azd up / azd down).
//
//   rg-<env>-hospital : the "hospital" - MediTrack + Discharge Copilot + gateway in ONE Container Apps environment,
//                       PostgreSQL (MediTrack's database), Azure Files (documents + import hot-folder),
//                       Azure AI Foundry (gpt-oss-20b), container registry
//   rg-<env>-poc      : the POC sandbox - Streamlit app with de-identified data, its own environment, no DB access
targetScope = 'subscription'

@minLength(1)
@maxLength(40)
@description('azd environment name, used in resource names')
param environmentName string

@description('Region for everything except (optionally) the model. Central India = Pune, matches the story.')
param location string = 'centralindia'

@secure()
@description('PostgreSQL admin password (letters and digits; set by the preprovision hook if empty)')
param pgAdminPassword string

@secure()
@description('Shared demo password: gateway basic auth (user "citycare") and the cloud POC')
param demoPassword string

@secure()
param logfireToken string = ''

@description('Optional: your public IP, allowed through the PostgreSQL firewall (for ./run.sh poc-export / warm against Azure)')
param clientIp string = ''

@description('Region of the Azure AI Foundry account (empty = same as location)')
param foundryLocation string = ''
param foundryModelName string = 'gpt-oss-20b'
param foundryModelFormat string = 'OpenAI-OSS'
param foundryModelVersion string = '1'
param foundrySkuName string = 'GlobalStandard'
param foundryCapacity int = 50

param meditrackExists bool = false
param copilotExists bool = false
param gatewayExists bool = false
param pocExists bool = false

var tags = { 'azd-env-name': environmentName, project: 'citycare-discharge-copilot' }
var token = toLower(uniqueString(subscription().id, environmentName, location))

resource hospitalRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${environmentName}-hospital'
  location: location
  tags: tags
}

resource pocRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${environmentName}-poc'
  location: location
  tags: tags
}

module hospital 'modules/hospital.bicep' = {
  name: 'hospital'
  scope: hospitalRg
  params: {
    location: location
    tags: tags
    token: token
    pgAdminPassword: pgAdminPassword
    demoPassword: demoPassword
    logfireToken: logfireToken
    clientIp: clientIp
    foundryLocation: empty(foundryLocation) ? location : foundryLocation
    foundryModelName: foundryModelName
    foundryModelFormat: foundryModelFormat
    foundryModelVersion: foundryModelVersion
    foundrySkuName: foundrySkuName
    foundryCapacity: foundryCapacity
    meditrackExists: meditrackExists
    copilotExists: copilotExists
    gatewayExists: gatewayExists
  }
}

module poc 'modules/poc.bicep' = {
  name: 'poc'
  scope: pocRg
  params: {
    location: location
    tags: tags
    token: token
    demoPassword: demoPassword
    logfireToken: logfireToken
    hospitalResourceGroup: hospitalRg.name
    registryLoginServer: hospital.outputs.registryLoginServer
    foundryAccountName: hospital.outputs.foundryAccountName
    foundryEndpoint: hospital.outputs.foundryEndpoint
    foundryDeployment: hospital.outputs.foundryDeployment
    pocExists: pocExists
  }
}

// POC's identity may pull images from the registry in the hospital RG
module pocAcrPull 'modules/acr-pull.bicep' = {
  name: 'poc-acr-pull'
  scope: hospitalRg
  params: {
    registryName: hospital.outputs.registryName
    principalId: poc.outputs.identityPrincipalId
  }
}

output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = hospitalRg.name
output AZURE_POC_RESOURCE_GROUP string = pocRg.name
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = hospital.outputs.registryLoginServer
output AZURE_CONTAINER_REGISTRY_NAME string = hospital.outputs.registryName
output MEDITRACK_URL string = hospital.outputs.gatewayUrl
output POC_URL string = poc.outputs.pocUrl
output RESET_JOB_NAME string = hospital.outputs.resetJobName
output POSTGRES_HOST string = hospital.outputs.postgresHost
output FOUNDRY_ACCOUNT_NAME string = hospital.outputs.foundryAccountName
output FOUNDRY_ENDPOINT string = hospital.outputs.foundryEndpoint
output FOUNDRY_DEPLOYMENT string = hospital.outputs.foundryDeployment
