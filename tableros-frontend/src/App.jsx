import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import PrivateRoute from './components/common/PrivateRoute'
import LoginPage    from './pages/LoginPage'
import HomePage     from './pages/HomePage'
import NoAutorizadoPage from './pages/NoAutorizadoPage'
import CallbackPage from './pages/CallbackPage'
import AdminDashboard from "./components/AdminDashboard";

function RootRedirect() {
  const { autenticado, cargando } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!cargando && autenticado) {
      navigate('/home', { replace: true, state: { loginExitoso: true } })
    }
  }, [autenticado, cargando, navigate])

  if (cargando) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Verificando sesión...</div>
  }

  if (autenticado) {
    return null
  }

  return <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/" element={<RootRedirect />} />

        <Route path="/login" element={<LoginPage />} />
        <Route path="/callback" element={<CallbackPage />} />

        <Route
          path="/home"
          element={
            <PrivateRoute>
              <HomePage />
            </PrivateRoute>
          }
        />

        {/* 2. AGREGAMOS LA RUTA PROTEGIDA DEL DASHBOARD */}
        <Route
          path="/admin-dashboard"
          element={
            <PrivateRoute>
              <AdminDashboard />
            </PrivateRoute>
          }
        />

        <Route
          path="/usuarios"
          element={
            <PrivateRoute roles={['admin']}>
              <HomePage />
            </PrivateRoute>
          }
        />

        <Route path="/no-autorizado" element={<NoAutorizadoPage />} />

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}