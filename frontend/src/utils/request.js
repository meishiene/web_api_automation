import axios from 'axios'

// 动态设置baseURL：如果是通过localhost访问，使用localhost:8000；否则使用当前域名的8000端口
const getBaseURL = () => {
  const currentOrigin = window.location.origin
  if (currentOrigin.includes('localhost') || currentOrigin.includes('127.0.0.1')) {
    return 'http://localhost:8000'
  } else {
    // 从当前origin提取协议和主机，然后替换端口为8000
    const url = new URL(currentOrigin)
    return `${url.protocol}//${url.hostname}:8000`
  }
}

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || getBaseURL(),
  timeout: 10000,
})

let isRefreshing = false
let pendingRequests = []

const clearAuthAndRedirect = () => {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('userId')
  localStorage.removeItem('username')
  window.location.href = '/login'
}

const processPendingRequests = (error, accessToken = null) => {
  pendingRequests.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(accessToken)
    }
  })
  pendingRequests = []
}

// Request interceptor - add Authorization header
request.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('accessToken')
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const originalRequest = error.config
    const isUnauthorized = error.response?.status === 401
    const isAuthEndpoint =
      originalRequest?.url?.includes('/api/auth/login') ||
      originalRequest?.url?.includes('/api/auth/refresh')

    if (!isUnauthorized || isAuthEndpoint) {
      return Promise.reject(error)
    }

    if (originalRequest._retry) {
      clearAuthAndRedirect()
      return Promise.reject(error)
    }

    originalRequest._retry = true
    const refreshToken = localStorage.getItem('refreshToken')
    if (!refreshToken) {
      clearAuthAndRedirect()
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingRequests.push({ resolve, reject })
      }).then((accessToken) => {
        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${accessToken}`
        return request(originalRequest)
      })
    }

    isRefreshing = true
    try {
      const baseURL = import.meta.env.VITE_API_BASE_URL || getBaseURL()
      const refreshResponse = await axios.post(
        `${baseURL}/api/auth/refresh`,
        { refresh_token: refreshToken },
        { timeout: 10000 }
      )
      const newAccessToken = refreshResponse.data.access_token
      localStorage.setItem('accessToken', newAccessToken)
      processPendingRequests(null, newAccessToken)
      originalRequest.headers = originalRequest.headers || {}
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
      return request(originalRequest)
    } catch (refreshError) {
      processPendingRequests(refreshError, null)
      clearAuthAndRedirect()
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

export default request
