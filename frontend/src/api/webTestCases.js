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

export const copyWebTestCase = (id, data = {}) => {
  return request.post(`/api/web-test-cases/${id}/copy`, data)
}

export const updateWebTestCase = (id, data) => {
  return request.put(`/api/web-test-cases/${id}`, data)
}

export const deleteWebTestCase = (id) => {
  return request.delete(`/api/web-test-cases/${id}`)
}

export const bulkDeleteWebTestCases = (projectId, data) => {
  return request.post(`/api/web-test-cases/project/${projectId}/bulk-delete`, data)
}

export const downloadWebTestCaseTemplate = (projectId) => {
  return request.get(`/api/web-test-cases/project/${projectId}/template.xlsx`, { responseType: 'blob' })
}

export const exportWebTestCases = (projectId) => {
  return request.get(`/api/web-test-cases/project/${projectId}/export.xlsx`, { responseType: 'blob' })
}

export const importWebTestCasesFromExcel = (projectId, data) => {
  return request.post(`/api/web-test-cases/project/${projectId}/import/xlsx`, data)
}
