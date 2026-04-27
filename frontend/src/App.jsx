import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar/Navbar'
import CVPage from './pages/CV/CVPage'
import PreferencesPage from './pages/Preferences/PreferencesPage'
import JobsPage from './pages/Jobs/JobsPage'
import TailoredCVPage from './pages/TailoredCV/TailoredCVPage'
import AuthPage from './pages/Auth/AuthPage'
import './App.css'

function Home() {
  return (
    <div className="home-page">
      <h1>FindMyJob</h1>
      <p className="home-subtitle">
        Your AI-powered job search assistant.
      </p>
    </div>
  )
}

function PrivateRoute({ children }) {
  const token = localStorage.getItem('access_token')
  return token ? children : <Navigate to="/login" replace />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<AuthPage />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <Navbar />
              <main className="page-shell">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/cv" element={<CVPage />} />
                  <Route path="/preferences" element={<PreferencesPage />} />
                  <Route path="/jobs" element={<JobsPage />} />
                  <Route path="/tailored-cvs" element={<TailoredCVPage />} />
                </Routes>
              </main>
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App

