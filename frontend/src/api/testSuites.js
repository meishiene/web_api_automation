import request from '@/utils/request'

export const getTestSuites = (projectId) => {
  return request.get(`/api/test-suites/project/${projectId}`)
}

export const createTestSuite = (projectId, payload) => {
  return request.post(`/api/test-suites/project/${projectId}`, payload)
}

export const updateTestSuite = (suiteId, payload) => {
  return request.put(`/api/test-suites/${suiteId}`, payload)
}

export const deleteTestSuite = (suiteId) => {
  return request.delete(`/api/test-suites/${suiteId}`)
}

export const getTestSuiteCases = (suiteId) => {
  return request.get(`/api/test-suites/${suiteId}/cases`)
}

export const upsertTestSuiteCase = (suiteId, caseId, payload) => {
  return request.post(`/api/test-suites/${suiteId}/cases/${caseId}`, payload)
}

export const deleteTestSuiteCase = (suiteId, caseId) => {
  return request.delete(`/api/test-suites/${suiteId}/cases/${caseId}`)
}

export const runTestSuite = (suiteId, payload = {}) => {
  return request.post(`/api/test-runs/suites/${suiteId}/run`, payload)
}
