import request from '@/utils/request'

export const getWebTestCases = (projectId) => {
  return request.get(`/api/web-test-cases/project/${projectId}`)
}

export const getWebTestCase = (id) => {
  return request.get(`/api/web-test-cases/${id}`)
}

export const createWebTestCase = (data) => {
  return request.post('/api/web-test-cases', data)
}

export const updateWebTestCase = (id, data) => {
  return request.put(`/api/web-test-cases/${id}`, data)
}

export const deleteWebTestCase = (id) => {
  return request.delete(`/api/web-test-cases/${id}`)
}

