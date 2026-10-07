// Returns the image an existing Container App runs, so re-provisioning doesn't roll it back to the placeholder.
param exists bool
param name string

resource existingApp 'Microsoft.App/containerApps@2024-03-01' existing = if (exists) {
  name: name
}

#disable-next-line BCP318
output image string = exists ? existingApp.properties.template.containers[0].image : ''
