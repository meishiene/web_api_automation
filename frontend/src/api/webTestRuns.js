import request from '@/utils/request'

export const runWebTestCase = (caseId) => {
  return request.post(`/api/web-test-runs/web-test-cases/${caseId}/run`)
}

export const getWebTestRuns = (projectId) => {
  return request.get(`/api/web-test-runs/project/${projectId}`)
}

export const getWebTestRunDetail = (runId) => {
  return request.get(`/api/web-test-runs/${runId}`)
}

