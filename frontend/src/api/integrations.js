import request from '@/utils/request'

export const getIntegrationGovernanceHealth = (projectId) => {
  return request.get(`/api/integrations/project/${projectId}/governance/health`)
}

export const retryIntegrationGovernanceBacklog = (projectId, payload = {}) => {
  return request.post(`/api/integrations/project/${projectId}/governance/retry-failed`, payload)
}
