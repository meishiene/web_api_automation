import request from '@/utils/request'

export const getUnifiedRuns = (projectId, params = {}) => {
  return request.get(`/api/test-runs/project/${projectId}/unified-results`, { params })
}
