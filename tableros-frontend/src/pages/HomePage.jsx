import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import Navbar from '../components/layout/Navbar'
import { getNombreCompleto } from '../auth/tokenStorage'

export default function HomePage() {
  const { usuarioCompleto, usuario } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [mensajeExito, setMensajeExito] = useState(!!location.state?.loginExitoso)

  useEffect(() => {
    if (mensajeExito) {
      const timer = setTimeout(() => setMensajeExito(false), 4000)
      return () => clearTimeout(timer)
    }
  }, [mensajeExito])

  const nombreCompleto =
    getNombreCompleto(usuarioCompleto) ||
    usuario?.correo_institucional ||
    usuario?.username ||
    ''

  return (
    <>
      <Navbar />
      <main style={styles.main}>
        {mensajeExito && (
          <div style={styles.bannerExito}>
            Inicio de sesión exitoso. ¡Bienvenido!
          </div>
        )}

        <h2 style={styles.titulo}>Bienvenido, {nombreCompleto}</h2>

        {/* ===== BOTÓN AGREGADO PARA IR AL DASHBOARD ===== */}
        <button 
          onClick={() => navigate('/admin-dashboard')} 
          style={styles.botonAdmin}
        >
          Bienvenido Administrador
        </button>
      </main>
    </>
  )
}

const styles = {
  main: {
    padding: '2rem',
    maxWidth: '800px',
    margin: '0 auto',
  },
  titulo: {
    color: '#1a1a2e',
    marginBottom: '1.5rem',
  },
  bannerExito: {
    backgroundColor: '#d4edda',
    color: '#155724',
    padding: '0.75rem 1rem',
    borderRadius: '6px',
    marginBottom: '1rem',
    border: '1px solid #c3e6cb',
    fontSize: '0.95rem',
  },
  // Estilo simple para el nuevo botón verde institucional
  botonAdmin: {
    backgroundColor: '#008f4c',
    color: '#ffffff',
    padding: '0.75rem 1.5rem',
    border: 'none',
    borderRadius: '6px',
    fontSize: '1rem',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginTop: '1rem',
    transition: 'background-color 0.2s',
  }
}