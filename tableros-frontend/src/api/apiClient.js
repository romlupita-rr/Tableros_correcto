import axios from 'axios'
import {
  getAccessToken,
  isTokenExpired,
  limpiarTokens,
  guardarAccessToken,
  buildLoginUrl,
} from '../auth/tokenStorage'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  async (config) => {
    const token = getAccessToken()
    if (token) {
      if (isTokenExpired()) {
        try {
          const { data } = await axios.post(
            `${config.baseURL || ''}/api/v1/auth/refresh`,
            {},
            { headers: { Authorization: `Bearer ${token}` } }
          )
          guardarAccessToken(data.accessToken, data.expiresIn)
          config.headers['Authorization'] = `Bearer ${data.accessToken}`
          return config
        } catch {
          limpiarTokens()
          window.location.href = buildLoginUrl()
          return Promise.reject(new Error('Sesión expirada'))
        }
      }
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    if (status === 401) {
      limpiarTokens()
      window.location.href = buildLoginUrl()
    }
    if (status === 403) {
      console.warn('[API] Acceso denegado:', error.response?.data?.detail)
    }
    return Promise.reject(error)
  }
)

export default apiClient
