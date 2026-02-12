import axios from 'axios'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
})

// Request interceptor - add X-User-ID header
request.interceptors.request.use(
  (config) => {
    const userId = localStorage.getItem('userId')
    if (userId) {
      config.headers['X-User-ID'] = userId
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
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('userId')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default request
