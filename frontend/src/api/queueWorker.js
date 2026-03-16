import request from '@/utils/request'

export const getQueueItems = (projectId, params = {}) => {
  return request.get(`/api/run-queue/project/${projectId}`, { params })
}

export const getQueueItemDetail = (queueItemId) => {
  return request.get(`/api/run-queue/${queueItemId}`)
}

export const getWorkerHeartbeats = (projectId) => {
  return request.get(`/api/run-queue/worker/heartbeats/project/${projectId}`)
}
