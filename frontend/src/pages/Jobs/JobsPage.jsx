import { useState } from 'react'
import { apiFetch } from '../../utils/api'
import './JobsPage.css'

const SOURCE_COLORS = {
  RemoteOK: '#12b76a',
  Arbeitnow: '#f79009',
  HN: '#ff6600',
  Adzuna: '#2e90fa',
}

function scoreColor(score) {
  if (score >= 70) return '#027a48'
  if (score >= 40) return '#b54708'
  return '#b42318'
}

function scoreBg(score) {
  if (score >= 70) return '#ecfdf3'
  if (score >= 40) return '#fffaeb'
  return '#fef3f2'
}

function JobCard({ job, onTailor }) {
  const [tailoring, setTailoring] = useState(false)
  const [tailorResult, setTailorResult] = useState(null)

  async function handleTailor() {
    setTailoring(true)
    setTailorResult(null)
    try {
      const res = await apiFetch('/api/cv/tailor/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_title: job.title || '',
          job_company: job.company || '',
          job_description: job.description || '',
        }),
      })
      if (res.ok) {
        setTailorResult({ success: true })
        if (onTailor) onTailor()
      } else {
        const data = await res.json()
        setTailorResult({ success: false, error: data.error || 'Tailoring failed.' })
      }
    } catch {
      setTailorResult({ success: false, error: 'Could not connect to server.' })
    } finally {
      setTailoring(false)
    }
  }

  return (
    <div className="job-card">
      <div className="job-card-header">
        <div className="job-title-row">
          <h3 className="job-title">{job.title}</h3>
          <span
            className="score-badge"
            style={{ color: scoreColor(job.score), background: scoreBg(job.score) }}
          >
            {job.score}% match
          </span>
        </div>

        <div className="job-meta">
          {job.company && <span className="job-company">{job.company}</span>}
          {job.company && job.location && <span className="meta-sep">·</span>}
          {job.location && <span className="job-location">{job.location}</span>}
          <span
            className="source-badge"
            style={{ background: SOURCE_COLORS[job.source] || '#667085' }}
          >
            {job.source}
          </span>
        </div>
      </div>

      {job.summary && (
        <p className="job-summary">{job.summary}</p>
      )}

      {job.tags && job.tags.length > 0 && (
        <div className="job-tags">
          {job.tags.slice(0, 6).map((tag) => (
            <span key={tag} className="job-tag">{tag}</span>
          ))}
        </div>
      )}

      <div className="job-card-actions">
        <a
          href={job.url}
          target="_blank"
          rel="noopener noreferrer"
          className="view-job-btn"
        >
          View Job →
        </a>

        <button
          className="tailor-btn"
          onClick={handleTailor}
          disabled={tailoring}
        >
          {tailoring ? 'Tailoring…' : '✨ Tailor CV'}
        </button>
      </div>

      {tailorResult && (
        <div className={`tailor-result ${tailorResult.success ? 'tailor-success' : 'tailor-error'}`}>
          {tailorResult.success
            ? <>CV tailored successfully! <a href="/tailored-cvs">View tailored CVs →</a></>
            : tailorResult.error}
        </div>
      )}
    </div>
  )
}

export default function JobsPage() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [searched, setSearched] = useState(false)

  async function handleSearch() {
    setLoading(true)
    setError('')
    setMessage('')
    setJobs([])

    try {
      const res = await apiFetch('/api/jobs/search/', { method: 'POST' })
      const data = await res.json()

      if (!res.ok) {
        setError(data.error || 'Something went wrong.')
        return
      }

      setJobs(data.jobs || [])
      setMessage(data.message || '')
      setSearched(true)
    } catch {
      setError('Could not connect to the server.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="jobs-page">
      <h1>Find Jobs</h1>
      <p className="jobs-subtitle">
        AI-powered job search based on your CV and preferences.
      </p>

      <button
        className="search-btn"
        onClick={handleSearch}
        disabled={loading}
      >
        {loading ? 'Searching & scoring…' : 'Search Jobs'}
      </button>

      {loading && (
        <div className="loading-state">
          <div className="spinner" />
          <p>Fetching listings and scoring them with AI — this may take a moment.</p>
        </div>
      )}

      {error && <div className="error-banner">{error}</div>}

      {!loading && searched && jobs.length === 0 && !error && (
        <div className="empty-state">
          <p>{message || 'No jobs found. Try adjusting your preferences.'}</p>
        </div>
      )}

      {jobs.length > 0 && (
        <div className="jobs-results">
          <p className="results-count">{jobs.length} jobs found, sorted by match score</p>
          <div className="jobs-list">
            {jobs.map((job, i) => (
              <JobCard key={`${job.source}-${i}`} job={job} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
