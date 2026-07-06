const ACCESS_TOKEN_KEY = 'tableros_access_token'
const EXPIRES_AT_KEY = 'tableros_token_expires_at'
const USER_KEY = 'tableros_user'

export function guardarAccessToken(accessToken, expiresIn) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
  localStorage.setItem(EXPIRES_AT_KEY, String(Date.now() + expiresIn * 1000))
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function guardarUsuario(usuario) {
  localStorage.setItem(USER_KEY, JSON.stringify(usuario))
}

export function getUsuarioAlmacenado() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function limpiarTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(EXPIRES_AT_KEY)
  localStorage.removeItem(USER_KEY)
}

export function isTokenExpired() {
  const expiresAt = localStorage.getItem(EXPIRES_AT_KEY)
  if (!expiresAt) return true
  return Date.now() > parseInt(expiresAt, 10) - 30000
}

export function decodeTokenPayload(token) {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(base64))
  } catch {
    return {}
  }
}

export function getRoles() {
  const user = getUsuarioAlmacenado()
  return user?.roles ?? []
}

export function tieneRol(rol) {
  return getRoles().includes(rol)
}

export function getNombreCompleto(usuario) {
  if (!usuario) return ''
  return [usuario.nombre, usuario.a_paterno, usuario.a_materno]
    .filter(Boolean)
    .join(' ')
}

export function buildLoginUrl() {
  const keycloakUrl = import.meta.env.VITE_KEYCLOAK_URL
  const realm = import.meta.env.VITE_KEYCLOAK_REALM
  const clientId = import.meta.env.VITE_KEYCLOAK_CLIENT_ID
  const redirectUri = 'http://localhost:8000/callback'
  const scope = 'openid profile email'

  const params = new URLSearchParams({
    response_type: 'code',
    client_id: clientId,
    redirect_uri: redirectUri,
    scope,
  })

  return `${keycloakUrl}/realms/${realm}/protocol/openid-connect/auth?${params.toString()}`
}

export function buildLogoutUrl() {
  const keycloakUrl = import.meta.env.VITE_KEYCLOAK_URL
  const realm = import.meta.env.VITE_KEYCLOAK_REALM
  const redirectUri = 'http://localhost:8000/login'

  const params = new URLSearchParams({
    redirect_uri: redirectUri,
  })

  return `${keycloakUrl}/realms/${realm}/protocol/openid-connect/logout?${params.toString()}`
}
