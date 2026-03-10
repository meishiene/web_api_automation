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
