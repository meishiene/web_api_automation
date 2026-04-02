import request from '@/utils/request'

export const getIntegrations = (projectId) => {
  return request.get(`/api/integrations/project/${projectId}`)
}

export const createIntegration = (projectId, payload) => {
  return request.post(`/api/integrations/project/${projectId}`, payload)
}

export const updateIntegration = (configId, payload) => {
  return request.put(`/api/integrations/${configId}`, payload)
}

export const deleteIntegration = (configId) => {
  return request.delete(`/api/integrations/${configId}`)
}

export const revealIntegrationCredential = (configId) => {
  return request.get(`/api/integrations/${configId}/credential-value`)
}

export const getIntegrationGovernanceHealth = (projectId) => {
  return request.get(`/api/integrations/project/${projectId}/governance/health`)
}

export const retryIntegrationGovernanceBacklog = (projectId, payload = {}) => {
  return request.post(`/api/integrations/project/${projectId}/governance/retry-failed`, payload)
}

export const getIntegrationGovernanceExecutions = (projectId, params = {}) => {
  return request.get(`/api/integrations/project/${projectId}/governance/executions`, { params })
}

export const createNotificationSubscription = (projectId, payload) => {
  return request.post(`/api/integrations/project/${projectId}/notification-subscriptions`, payload)
}

export const getNotificationSubscriptions = (projectId, params = {}) => {
  return request.get(`/api/integrations/project/${projectId}/notification-subscriptions`, { params })
}

export const dispatchNotification = (subscriptionId, payload) => {
  return request.post(`/api/integrations/notification-subscriptions/${subscriptionId}/dispatch`, payload)
}

export const getNotificationDeliveries = (projectId, params = {}) => {
  return request.get(`/api/integrations/project/${projectId}/notification-deliveries`, { params })
}

export const retryNotificationDelivery = (deliveryId) => {
  return request.post(`/api/integrations/notification-deliveries/${deliveryId}/retry`)
}

export const getDefectSyncRecords = (projectId, params = {}) => {
  return request.get(`/api/integrations/project/${projectId}/defects/records`, { params })
}

export const getIdentityBindings = (configId, params = {}) => {
  return request.get(`/api/integrations/${configId}/identity/bindings`, { params })
}

export const getCicdRuns = (configId, params = {}) => {
  return request.get(`/api/integrations/${configId}/cicd/runs`, { params })
}
