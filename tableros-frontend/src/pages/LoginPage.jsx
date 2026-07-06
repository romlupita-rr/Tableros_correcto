import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function LoginPage() {
  const { autenticado, cargando, login } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!cargando && autenticado) {
      navigate('/home', { replace: true })
    }
  }, [autenticado, cargando, navigate])

  if (cargando) {
    return (
      <div style={styles.contenedor}>
        <p style={{ color: '#fff' }}>Verificando sesión...</p>
      </div>
    )
  }

  return (
    <div style={styles.contenedor}>
      <div style={styles.tarjeta}>
        <img
          src="/logo.png"
          alt="CONALEP"
          style={styles.logo}
          onError={(e) => { e.currentTarget.style.display = 'none' }}
        />

        <h2 style={styles.headerPrincipal}>Colegio Nacional de Educación Profesional Técnica</h2>
        <p style={styles.headerSecundario}>Sistema Tableros Academicos</p>

        <div style={styles.separador} />

        <h1 style={styles.titulo}>Bienvenido</h1>
        <p style={styles.subtitulo}>Inicie sesión para acceder al sistema</p>

        <button style={styles.boton} onClick={login}>
          Iniciar Sesión
        </button>
      </div>

      <footer style={styles.footer}>
        CONALEP © 2026 — Todos los derechos reservados
      </footer>
    </div>
  )
}

const styles = {
  contenedor: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#007E67',
    padding: '1rem',
    position: 'relative',
  },
  tarjeta: {
    backgroundColor: '#fff',
    padding: '3rem 3.5rem',
    borderRadius: '16px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.25)',
    textAlign: 'center',
    maxWidth: '440px',
    width: '100%',
  },
  logo: {
    width: '220px',
    height: 'auto',
    marginBottom: '1.5rem',
  },
  headerPrincipal: {
    margin: '0 0 0.5rem',
    fontSize: '0.95rem',
    fontWeight: 600,
    color: '#1a1a1a',
    lineHeight: 1.4,
  },
  headerSecundario: {
    margin: '0 0 0.5rem',
    fontSize: '0.85rem',
    color: '#757575',
  },
  separador: {
    borderTop: '1px solid #e0e0e0',
    margin: '1.5rem 0',
  },
  titulo: {
    margin: '0 0 0.5rem',
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#1a1a1a',
  },
  subtitulo: {
    margin: '0 0 2rem',
    fontSize: '0.95rem',
    color: '#757575',
  },
  boton: {
    width: '100%',
    padding: '0.85rem',
    backgroundColor: '#007E67',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  footer: {
    position: 'absolute',
    bottom: '1.5rem',
    color: '#fff',
    fontSize: '0.8rem',
    opacity: 0.9,
  },
}
