import request from '@/utils/request'

export const getTestCases = (projectId, params = {}) => {
  return request.get(`/api/test-cases/project/${projectId}`, { params })
}

export const exportTestCases = (projectId) => {
  return request.get(`/api/test-cases/project/${projectId}/export`)
}

export const importTestCases = (projectId, data) => {
  return request.post(`/api/test-cases/project/${projectId}/import`, data)
}

export const importOpenApiTestCases = (projectId, data) => {
  return request.post(`/api/test-cases/project/${projectId}/import/openapi`, data)
}

export const getImportProviders = () => {
  return request.get('/api/test-cases/import/providers')
}

export const importTestCasesByProvider = (projectId, data) => {
  return request.post(`/api/test-cases/project/${projectId}/import/provider`, data)
}

export const createTestCase = (projectId, data) => {
  return request.post(`/api/test-cases/project/${projectId}`, data)
}

export const copyTestCase = (projectId, id, data = {}) => {
  return request.post(`/api/test-cases/${id}/copy`, data)
}

export const updateTestCase = (projectId, id, data) => {
  return request.put(`/api/test-cases/${id}`, data)
}

export const deleteTestCase = (projectId, id) => {
  return request.delete(`/api/test-cases/${id}`)
}

export const runTestCase = (projectId, id, data) => {
  return request.post(`/api/test-runs/test-cases/${id}/run`, data)
}

export const getTestResult = (projectId, runId) => {
  return request.get(`/api/test-runs/${runId}`)
}
