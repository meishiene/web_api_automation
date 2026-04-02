import request from '@/utils/request'

export const getProjects = () => {
  return request.get('/api/projects')
}

export const createProject = (data) => {
  return request.post('/api/projects', data)
}

export const updateProject = (id, data) => {
  return request.put(`/api/projects/${id}`, data)
}

export const deleteProject = (id) => {
  return request.delete(`/api/projects/${id}`)
}

export const getProjectMembers = (projectId) => {
  return request.get(`/api/projects/${projectId}/members`)
}

export const upsertProjectMember = (projectId, payload) => {
  return request.post(`/api/projects/${projectId}/members`, payload)
}

export const deleteProjectMember = (projectId, userId) => {
  return request.delete(`/api/projects/${projectId}/members/${userId}`)
}
