import { useContext } from 'react'
import { AuthContext } from '../context/AuthContext'

/**
 * Hook para acceder al estado de autenticación desde cualquier componente.
 *
 * Uso:
 *   const { autenticado, usuario, cargando, login, logout } = useAuth()
 *
 * Propiedades disponibles:
 *   autenticado  {boolean}  — true si el usuario tiene sesión activa en Keycloak
 *   usuario      {object}   — { username, email, nombreCompleto, roles }
 *   cargando     {boolean}  — true mientras Keycloak verifica la sesión inicial
 *   login        {function} — redirige a la pantalla de login de Keycloak
 *   logout       {function} — cierra sesión y redirige al origen
 */
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  }
  return context
}
