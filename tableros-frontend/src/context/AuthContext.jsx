import { createContext, useState, useEffect } from 'react'
import {
  getAccessToken,
  getUsuarioAlmacenado,
  isTokenExpired,
  limpiarTokens,
  buildLoginUrl,
  buildLogoutUrl,
  guardarAccessToken,
  guardarUsuario,
} from '../auth/tokenStorage'
import apiClient from '../api/apiClient'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [autenticado, setAutenticado] = useState(false)
  const [usuario, setUsuario] = useState(null)
  const [usuarioCompleto, setUsuarioCompleto] = useState(null)
  const [roles, setRoles] = useState([])
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    const token = getAccessToken()
    const user = getUsuarioAlmacenado()
    if (token && !isTokenExpired() && user) {
      setUsuario(user)
      setRoles(user.roles || [])
      setAutenticado(true)
      cargarUsuarioCompleto()
    }
    setCargando(false)
  }, [])

  const login = () => {
    window.location.href = buildLoginUrl()
  }

  const cargarUsuarioCompleto = async () => {
    try {
      const { data } = await apiClient.get('/api/v1/auth/me')
      setUsuarioCompleto(data)
      return data
    } catch (err) {
      console.error('[Auth] Error al cargar usuario completo:', err)
      return null
    }
  }

  const handleLoginSuccess = ({ accessToken, expiresIn, user }) => {
    guardarAccessToken(accessToken, expiresIn)
    guardarUsuario(user)
    setUsuario(user)
    setRoles(user.roles || [])
    setAutenticado(true)
    cargarUsuarioCompleto()
  }

  const logout = async () => {
    limpiarTokens()
    setUsuario(null)
    setUsuarioCompleto(null)
    setRoles([])
    setAutenticado(false)
    window.location.href = buildLogoutUrl()
  }

  return (
    <AuthContext.Provider
      value={{
        autenticado,
        usuario,
        usuarioCompleto,
        roles,
        cargando,
        login,
        logout,
        handleLoginSuccess,
        cargarUsuarioCompleto,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
