import { useAuth } from '../../hooks/useAuth'

/**
 * Renderiza children solo si el usuario tiene al menos uno de los roles indicados.
 *
 * Uso:
 *   <RoleGuard roles={['admin']}>
 *     <button>Eliminar usuario</button>
 *   </RoleGuard>
 */
export default function RoleGuard({ roles = [], children, fallback = null }) {
  const { roles: userRoles } = useAuth()

  if (!roles || roles.length === 0) return children

  const tieneAcceso = roles.some((r) => userRoles.includes(r))
  return tieneAcceso ? children : fallback
}
