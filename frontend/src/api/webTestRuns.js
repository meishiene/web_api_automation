import request from '@/utils/request'

const EXECUTION_TIMEOUT_MS = 10 * 60 * 1000

export const runWebTestCase = (caseId) => {
  return request.post(`/api/web-test-runs/web-test-cases/${caseId}/run`, null, {
    timeout: EXECUTION_TIMEOUT_MS,
  })
}

export const runBatchWebTestCases = (projectId, data) => {
  return request.post(`/api/web-test-runs/project/${projectId}/batch-run`, data, {
    timeout: EXECUTION_TIMEOUT_MS,
  })
}

export const getWebBatchRuns = (projectId) => {
  return request.get(`/api/web-test-runs/batches/project/${projectId}`)
}

export const getWebBatchRunDetail = (batchId) => {
  return request.get(`/api/web-test-runs/batches/${batchId}`)
}

export const getWebTestRuns = (projectId) => {
  return request.get(`/api/web-test-runs/project/${projectId}`)
}

export const getWebTestRunDetail = (runId) => {
  return request.get(`/api/web-test-runs/${runId}`)
}
