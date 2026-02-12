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
