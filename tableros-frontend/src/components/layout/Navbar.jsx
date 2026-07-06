import { useAuth } from '../../hooks/useAuth'
import { getNombreCompleto } from '../../auth/tokenStorage'

/**
 * Barra de navegación superior.
 * Muestra el nombre del usuario autenticado y el botón de cerrar sesión.
 */
export default function Navbar() {
  const { usuarioCompleto, usuario, logout } = useAuth()

  const nombre =
    getNombreCompleto(usuarioCompleto) ||
    usuario?.correo_institucional ||
    usuario?.username ||
    '...'

  return (
    <nav style={styles.nav}>
      <span style={styles.titulo}>Mi Sistema</span>

      <div style={styles.usuario}>
        <span style={styles.nombre}>{nombre}</span>
        <button style={styles.botonLogout} onClick={logout}>
          Cerrar sesión
        </button>
      </div>
    </nav>
  )
}

const styles = {
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '0.75rem 1.5rem',
    backgroundColor: '#1a1a2e',
    color: '#fff',
  },
  titulo: {
    fontSize: '1.1rem',
    fontWeight: 'bold',
  },
  usuario: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
  },
  nombre: {
    fontSize: '0.9rem',
    color: '#ccc',
  },
  botonLogout: {
    padding: '0.4rem 0.9rem',
    backgroundColor: '#e74c3c',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.85rem',
  },
}
