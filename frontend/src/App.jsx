import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import Navbar from './components/Navbar/Navbar'
import CVPage from './pages/CV/CVPage'
import PreferencesPage from './pages/Preferences/PreferencesPage'
import JobsPage from './pages/Jobs/JobsPage'
import TailoredCVPage from './pages/TailoredCV/TailoredCVPage'
import CoverLettersPage from './pages/CoverLetters/CoverLettersPage'
import ApplicationsPage from './pages/Applications/ApplicationsPage'
import AuthPage from './pages/Auth/AuthPage'
import './App.css'

const STEPS = [
  { number: '01', title: 'Upload your CV', desc: 'We parse your skills, experience and education automatically.' },
  { number: '02', title: 'Set preferences', desc: 'Pick job title, location, seniority and which sources to search.' },
  { number: '03', title: 'AI finds & scores', desc: 'We query RemoteOK, Arbeitnow and HN, then score every listing against your CV.' },
  { number: '04', title: 'Apply with confidence', desc: 'Tailor your CV per job, generate a cover letter, and track your applications.' },
]

const FEATURES = [
  { icon: '🤖', title: 'AI Match Score', desc: 'Every job gets a 0–100 match score based on your exact CV, so you apply where you actually fit.' },
  { icon: '✨', title: 'CV Tailoring', desc: 'Rewrite your bullet points to mirror job keywords — without fabricating anything.' },
  { icon: '📝', title: 'Cover Letters', desc: 'Generate a personalised cover letter for any listing in seconds.' },
  { icon: '📬', title: 'Email Digests', desc: 'Get your top matches delivered daily or weekly so you never miss an opportunity.' },
  { icon: '📊', title: 'Application Tracker', desc: 'Kanban-style board to track every job as Saved, Applied or Rejected.' },
  { icon: '⚡', title: 'Smart Caching', desc: 'Results are cached per source so repeated searches are instant and APIs are never called twice.' },
]

function Home() {
  const navigate = useNavigate()
  return (
    <div className="home-page">
      {/* ── Hero ── */}
      <div className="hero">
        <div className="hero-badge">AI-Powered Job Search</div>
        <h1 className="hero-title">
          Find jobs that actually<br />
          <span className="hero-accent">match your skills</span>
        </h1>
        <p className="hero-subtitle">
          Upload your CV, set your preferences, and let our AI score every listing
          against your profile — so you spend time applying, not scrolling.
        </p>
        <div className="hero-actions">
          <button className="btn-primary" onClick={() => navigate('/jobs')}>Search Jobs →</button>
          <button className="btn-secondary" onClick={() => navigate('/cv')}>Upload CV</button>
        </div>
      </div>

      {/* ── How it works ── */}
      <div className="section">
        <h2 className="section-title">How it works</h2>
        <div className="steps-grid">
          {STEPS.map(s => (
            <div className="step-card" key={s.number}>
              <div className="step-number">{s.number}</div>
              <h3 className="step-title">{s.title}</h3>
              <p className="step-desc">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Features ── */}
      <div className="section">
        <h2 className="section-title">Everything you need</h2>
        <div className="features-grid">
          {FEATURES.map(f => (
            <div className="feature-card" key={f.title}>
              <div className="feature-icon">{f.icon}</div>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
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
                  <Route path="/tailored-cvs/:id" element={<TailoredCVPage />} />
                  <Route path="/cover-letters" element={<CoverLettersPage />} />
                  <Route path="/applications" element={<ApplicationsPage />} />
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

