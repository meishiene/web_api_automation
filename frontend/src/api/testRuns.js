import request from '@/utils/request'

export const getBatchRuns = (projectId) => {
  return request.get(`/api/test-runs/batches/project/${projectId}`)
}

export const getBatchRunDetail = (batchId) => {
  return request.get(`/api/test-runs/batches/${batchId}`)
}

export const getTestRunDetail = (runId) => {
  return request.get(`/api/test-runs/${runId}`)
}
