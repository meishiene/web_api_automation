const ACTIVE_PROJECT_STORAGE_KEY = 'ttapi-active-project-id'

export const getActiveProjectId = () => {
  const raw = localStorage.getItem(ACTIVE_PROJECT_STORAGE_KEY)
  if (!raw) return null
  const parsed = Number(raw)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
}

export const setActiveProjectId = (projectId) => {
  const parsed = Number(projectId)
  if (!Number.isFinite(parsed) || parsed <= 0) {
    localStorage.removeItem(ACTIVE_PROJECT_STORAGE_KEY)
    return
  }
  localStorage.setItem(ACTIVE_PROJECT_STORAGE_KEY, String(parsed))
}

export const clearActiveProjectId = () => {
  localStorage.removeItem(ACTIVE_PROJECT_STORAGE_KEY)
}
