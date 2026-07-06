import { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import axios from 'axios'
import { useAuth } from '../hooks/useAuth'

export default function CallbackPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { handleLoginSuccess } = useAuth()
  const [error, setError] = useState(null)
  const ejecutado = useRef(false)

  useEffect(() => {
    if (ejecutado.current) return
    ejecutado.current = true

    const code = searchParams.get('code')
    if (!code) {
      setError('No se recibió el código de autorización')
      return
    }

    const baseURL = import.meta.env.VITE_API_BASE_URL || ''
    const redirectUri = `${window.location.origin}/callback`

    axios
      .post(`${baseURL}/api/v1/auth/login`, { code, redirectUri })
      .then(({ data }) => {
        handleLoginSuccess(data)
        navigate('/home', { replace: true, state: { loginExitoso: true } })
      })
      .catch((err) => {
        const msg = err.response?.data?.detail ?? err.message ?? 'Error al iniciar sesión'
        setError(msg)
      })
  }, [searchParams, navigate, handleLoginSuccess])

  if (error) {
    return (
      <div style={styles.contenedor}>
        <div style={styles.tarjeta}>
          <h2 style={styles.errorTitulo}>Error de autenticación</h2>
          <p style={styles.errorMsg}>{error}</p>
          <button style={styles.boton} onClick={() => navigate('/login')}>
            Volver al inicio
          </button>
        </div>
      </div>
    )
  }

  return (
    <div style={styles.contenedor}>
      <p>Iniciando sesión...</p>
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
    padding: '2rem',
    borderRadius: '8px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
    textAlign: 'center',
    maxWidth: '400px',
  },
  errorTitulo: {
    color: '#e74c3c',
    marginBottom: '0.5rem',
  },
  errorMsg: {
    color: '#666',
    marginBottom: '1.5rem',
  },
  boton: {
    padding: '0.6rem 1.2rem',
    backgroundColor: '#1a1a2e',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
}
