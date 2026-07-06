import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { AuthProvider } from './context/AuthContext'
import App from './App'

/**
 * Punto de entrada de la aplicación.
 *
 * AuthProvider envuelve todo para que cualquier componente
 * pueda acceder al estado de autenticación via useAuth().
 *
 * Nota: StrictMode está habilitado. AuthContext usa un ref
 * para evitar la doble inicialización de Keycloak que esto provoca.
 */
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>
)
