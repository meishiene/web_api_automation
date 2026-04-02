import request from '@/utils/request'

export const getScheduleTasks = (projectId) => {
  return request.get(`/api/schedule-tasks/project/${projectId}`)
}

export const createScheduleTask = (payload) => {
  return request.post('/api/schedule-tasks', payload)
}

export const updateScheduleTask = (taskId, payload) => {
  return request.put(`/api/schedule-tasks/${taskId}`, payload)
}

export const deleteScheduleTask = (taskId) => {
  return request.delete(`/api/schedule-tasks/${taskId}`)
}

export const triggerScheduleTask = (taskId) => {
  return request.post(`/api/schedule-tasks/${taskId}/trigger`)
}
