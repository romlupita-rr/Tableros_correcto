import { useAuth } from '../hooks/useAuth'

export default function NoAutorizadoPage() {
  const { logout } = useAuth()

  return (
    <div style={styles.contenedor}>
      <div style={styles.tarjeta}>
        <div style={styles.icono}>!</div>
        <h1 style={styles.titulo}>Acceso denegado</h1>
        <p style={styles.mensaje}>
          Usted no tiene autorización de usar este sistema.
        </p>
        <p style={styles.submensaje}>
          Si crees que esto es un error, contacta al administrador.
        </p>
        <button style={styles.boton} onClick={logout}>
          Cerrar sesión
        </button>
      </div>
    </div>
  )
}

const styles = {
  contenedor: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    backgroundColor: '#f0f2f5',
  },
  tarjeta: {
    backgroundColor: '#fff',
    padding: '2.5rem 3rem',
    borderRadius: '8px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
    textAlign: 'center',
    maxWidth: '420px',
  },
  icono: {
    width: '60px',
    height: '60px',
    borderRadius: '50%',
    backgroundColor: '#e74c3c',
    color: '#fff',
    fontSize: '2rem',
    fontWeight: 'bold',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 1rem',
  },
  titulo: {
    margin: '0 0 0.5rem',
    fontSize: '1.5rem',
    color: '#1a1a2e',
  },
  mensaje: {
    color: '#555',
    fontSize: '1rem',
    marginBottom: '0.5rem',
  },
  submensaje: {
    color: '#888',
    fontSize: '0.85rem',
    marginBottom: '1.5rem',
  },
  boton: {
    padding: '0.6rem 1.2rem',
    backgroundColor: '#1a1a2e',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.9rem',
  },
}
