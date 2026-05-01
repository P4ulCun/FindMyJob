import { useState, useEffect } from 'react'
import { apiFetch } from '../../utils/api'
import './ApplicationsPage.css'

export default function ApplicationsPage() {
  const [interactions, setInteractions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchInteractions() {
      try {
        const res = await apiFetch('/api/jobs/interactions/')
        if (!res.ok) {
          setError('Failed to fetch job interactions.')
          return
        }
        const data = await res.json()
        setInteractions(data.interactions || [])
      } catch (err) {
        setError('Could not connect to the server.')
      } finally {
        setLoading(false)
      }
    }
    fetchInteractions()
  }, [])

  const grouped = {
    applied: interactions.filter(i => i.status === 'applied'),
    saved: interactions.filter(i => i.status === 'saved'),
    rejected: interactions.filter(i => i.status === 'rejected'),
  }

  if (loading) {
    return (
      <div className="applications-page">
        <h1>My Applications</h1>
        <div className="loading-state">
          <div className="spinner" />
          <p>Loading your jobs...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="applications-page">
      <h1>My Applications</h1>
      <p className="applications-subtitle">
        Track the jobs you've interacted with.
      </p>

      {error && <div className="error-banner">{error}</div>}

      {!error && interactions.length === 0 && (
        <div className="empty-state">
          <p>You haven't tracked any jobs yet. Go to Find Jobs and mark some!</p>
        </div>
      )}

      {interactions.length > 0 && (
        <div className="pipeline-board">
          <div className="pipeline-column applied-col">
            <h2 className="col-title">Applied <span>({grouped.applied.length})</span></h2>
            <div className="col-items">
              {grouped.applied.map(job => <TrackedJobCard key={job.id} job={job} />)}
            </div>
          </div>

          <div className="pipeline-column saved-col">
            <h2 className="col-title">Saved <span>({grouped.saved.length})</span></h2>
            <div className="col-items">
              {grouped.saved.map(job => <TrackedJobCard key={job.id} job={job} />)}
            </div>
          </div>

          <div className="pipeline-column rejected-col">
            <h2 className="col-title">Rejected <span>({grouped.rejected.length})</span></h2>
            <div className="col-items">
              {grouped.rejected.map(job => <TrackedJobCard key={job.id} job={job} />)}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function TrackedJobCard({ job }) {
  const dateStr = new Date(job.updated_at).toLocaleDateString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric'
  })

  return (
    <div className="tracked-job-card">
      <h3 className="tj-title">{job.job_title}</h3>
      <div className="tj-meta">
        {job.job_company && <span className="tj-company">{job.job_company}</span>}
        {job.job_location && (
          <>
            <span className="meta-sep">·</span>
            <span className="tj-location">{job.job_location}</span>
          </>
        )}
      </div>
      <div className="tj-footer">
        <span className="tj-date">{dateStr}</span>
        <a href={job.job_url} target="_blank" rel="noopener noreferrer" className="tj-link">
          View
        </a>
      </div>
    </div>
  )
}
