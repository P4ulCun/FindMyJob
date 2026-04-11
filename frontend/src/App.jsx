import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import CVPage from './pages/CV/CVPage'
import PreferencesPage from './pages/Preferences/PreferencesPage'
import './App.css'

function Home() {
  return (
    <div className="app">
      <h1>FindMyJob</h1>
      <p className="read-the-docs">
        React + Vite + Django + PostgreSQL
      </p>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <nav className="main-nav">
        <Link to="/">Home</Link>
        <Link to="/cv">Upload CV</Link>
        <Link to="/preferences">Preferences</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/cv" element={<CVPage />} />
        <Route path="/preferences" element={<PreferencesPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
