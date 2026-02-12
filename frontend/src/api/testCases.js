import request from '@/utils/request'

export const getTestCases = (projectId) => {
  return request.get(`/api/test-cases/project/${projectId}`)
}

export const createTestCase = (projectId, data) => {
  return request.post(`/api/test-cases/project/${projectId}`, data)
}

export const updateTestCase = (projectId, id, data) => {
  return request.put(`/api/test-cases/${id}`, data)
}

export const deleteTestCase = (projectId, id) => {
  return request.delete(`/api/test-cases/${id}`)
}

export const runTestCase = (projectId, id) => {
  return request.post(`/api/test-runs/test-cases/${id}/run`)
}

export const getTestResult = (projectId, runId) => {
  return request.get(`/api/test-runs/${runId}`)
}
