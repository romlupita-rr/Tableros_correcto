import keycloak from '../auth/keycloak'

/**
 * Retorna el token JWT actual (string) para usarlo manualmente si es necesario.
 */
export const getToken = () => keycloak.token ?? null

/**
 * Retorna el payload decodificado del token actual.
 */
export const getTokenParsed = () => keycloak.tokenParsed ?? null

/**
 * Verifica si el usuario tiene un rol específico en el realm de Keycloak.
 *
 * Uso:
 *   if (tieneRol('admin')) { ... }
 */
export const tieneRol = (rol) => {
  return keycloak.tokenParsed?.realm_access?.roles?.includes(rol) ?? false
}

/**
 * Verifica si el usuario tiene alguno de los roles indicados.
 *
 * Uso:
 *   if (tieneAlgunRol(['admin', 'consulta'])) { ... }
 */
export const tieneAlgunRol = (roles = []) => {
  return roles.some((rol) => tieneRol(rol))
}
