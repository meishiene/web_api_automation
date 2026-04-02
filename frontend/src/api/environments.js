import request from '@/utils/request'

export const getProjectEnvironments = (projectId) => request.get(`/api/environments/project/${projectId}`)

export const createProjectEnvironment = (projectId, payload) =>
  request.post(`/api/environments/project/${projectId}`, payload)

export const updateProjectEnvironment = (environmentId, payload) =>
  request.put(`/api/environments/${environmentId}`, payload)

export const deleteProjectEnvironment = (environmentId) =>
  request.delete(`/api/environments/${environmentId}`)

export const getProjectVariables = (projectId) => request.get(`/api/environments/project/${projectId}/variables`)

export const upsertProjectVariable = (projectId, payload) =>
  request.post(`/api/environments/project/${projectId}/variables`, payload)

export const getProjectVariableGroups = (projectId) =>
  request.get(`/api/environments/project/${projectId}/variable-groups`)

export const revealProjectSecret = (projectId, key) =>
  request.get(`/api/environments/project/${projectId}/variables/${encodeURIComponent(key)}/secret-value`)

export const getEnvironmentVariables = (environmentId) => request.get(`/api/environments/${environmentId}/variables`)

export const upsertEnvironmentVariable = (environmentId, payload) =>
  request.post(`/api/environments/${environmentId}/variables`, payload)

export const getEnvironmentVariableGroups = (environmentId) =>
  request.get(`/api/environments/${environmentId}/variable-groups`)

export const bindEnvironmentVariableGroup = (environmentId, groupName) =>
  request.post(`/api/environments/${environmentId}/variable-groups/bind`, { group_name: groupName })

export const unbindEnvironmentVariableGroup = (environmentId, groupName) =>
  request.delete(`/api/environments/${environmentId}/variable-groups/bind/${encodeURIComponent(groupName)}`)

export const revealEnvironmentSecret = (environmentId, key) =>
  request.get(`/api/environments/${environmentId}/variables/${encodeURIComponent(key)}/secret-value`)
