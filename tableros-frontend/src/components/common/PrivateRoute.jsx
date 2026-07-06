import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

/**
 * Protege rutas privadas.
 *
 * Uso:
 *   <PrivateRoute>
 *     <HomePage />
 *   </PrivateRoute>
 *
 *   <PrivateRoute roles={['admin']}>
 *     <AdminPage />
 *   </PrivateRoute>
 *
 * - Si está cargando                  → pantalla de carga
 * - Si no está autenticado            → redirige a /login
 * - Si requiere roles y no los tiene  → redirige a /no-autorizado
 */
export default function PrivateRoute({ children, roles }) {
  const { autenticado, roles: userRoles, cargando } = useAuth()

  if (cargando) {
    return (
      <div style={styles.contenedor}>
        <p style={styles.texto}>Verificando sesión...</p>
      </div>
    )
  }

  if (!autenticado) {
    return <Navigate to="/login" replace />
  }

  if (roles && roles.length > 0) {
    const tieneAcceso = roles.some((r) => userRoles.includes(r))
    if (!tieneAcceso) {
      return <Navigate to="/no-autorizado" replace />
    }
  }

  return children
}

const styles = {
  contenedor: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
  },
  texto: {
    fontSize: '1.1rem',
    color: '#555',
  },
}
