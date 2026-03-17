import request from '@/utils/request'

export const getProjectReportSummary = (projectId, params = {}) => {
  return request.get(`/api/reports/project/${projectId}/summary`, { params })
}

export const getProjectReportTrends = (projectId, params = {}) => {
  return request.get(`/api/reports/project/${projectId}/trends`, { params })
}

export const getProjectReportFailures = (projectId, params = {}) => {
  return request.get(`/api/reports/project/${projectId}/failures`, { params })
}
