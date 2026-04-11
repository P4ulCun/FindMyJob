import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar/Navbar'
import CVPage from './pages/CV/CVPage'
import PreferencesPage from './pages/Preferences/PreferencesPage'
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

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main className="page-shell">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/cv" element={<CVPage />} />
          <Route path="/preferences" element={<PreferencesPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App
