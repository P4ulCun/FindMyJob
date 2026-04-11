import { useState, useEffect } from 'react';
import './PreferencesPage.css';

const API_PREFERENCES = '/api/preferences/';

function authHeaders(extra = {}) {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}`, ...extra } : { ...extra };
}

const WORK_TYPES = [
  { value: 'remote', label: 'Remote' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'on-site', label: 'On-site' },
];

const SENIORITY_LEVELS = [
  { value: 'junior', label: 'Junior' },
  { value: 'mid', label: 'Mid' },
  { value: 'senior', label: 'Senior' },
];

const INITIAL = {
  job_title: '',
  location: '',
  work_type: '',
  seniority: '',
};

export default function PreferencesPage() {
  const [form, setForm] = useState(INITIAL);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // ---- fetch on mount ----
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(API_PREFERENCES, {
          headers: authHeaders(),
        });
        if (!res.ok) {
          setError('Could not load preferences.');
          return;
        }
        const data = await res.json();
        setForm({
          job_title: data.job_title ?? '',
          location: data.location ?? '',
          work_type: data.work_type ?? '',
          seniority: data.seniority ?? '',
        });
      } catch {
        setError('Network error — could not reach the server.');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // ---- field change ----
  const update = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setSuccess('');
  };

  // ---- save ----
  const handleSave = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      const res = await fetch(API_PREFERENCES, {
        method: 'PUT',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) {
        const msg =
          data.non_field_errors?.[0] ||
          data.detail ||
          Object.values(data).flat().join(' ') ||
          'Save failed.';
        setError(msg);
        return;
      }
      setSuccess('Preferences saved successfully.');
    } catch {
      setError('Network error — could not reach the server.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="pref-page">
        <h1>Job Preferences</h1>
        <p className="pref-loading">Loading…</p>
      </div>
    );
  }

  return (
    <div className="pref-page">
      <h1>Job Preferences</h1>

      <form className="pref-form" onSubmit={handleSave}>
        {/* Job Title */}
        <div className="pref-field">
          <label htmlFor="job_title">Job Title</label>
          <input
            id="job_title"
            type="text"
            placeholder="e.g. Frontend Developer"
            value={form.job_title}
            onChange={(e) => update('job_title', e.target.value)}
          />
        </div>

        {/* Location */}
        <div className="pref-field">
          <label htmlFor="location">Location</label>
          <input
            id="location"
            type="text"
            placeholder="e.g. Bucharest, Romania"
            value={form.location}
            onChange={(e) => update('location', e.target.value)}
          />
        </div>

        {/* Work Type */}
        <fieldset className="pref-fieldset">
          <legend>Work Type</legend>
          <div className="pref-radio-group">
            {WORK_TYPES.map((wt) => (
              <label
                key={wt.value}
                className={`pref-radio-card${form.work_type === wt.value ? ' selected' : ''}`}
              >
                <input
                  type="radio"
                  name="work_type"
                  value={wt.value}
                  checked={form.work_type === wt.value}
                  onChange={() => update('work_type', wt.value)}
                />
                <span>{wt.label}</span>
              </label>
            ))}
          </div>
        </fieldset>

        {/* Seniority */}
        <fieldset className="pref-fieldset">
          <legend>Seniority</legend>
          <div className="pref-radio-group">
            {SENIORITY_LEVELS.map((s) => (
              <label
                key={s.value}
                className={`pref-radio-card${form.seniority === s.value ? ' selected' : ''}`}
              >
                <input
                  type="radio"
                  name="seniority"
                  value={s.value}
                  checked={form.seniority === s.value}
                  onChange={() => update('seniority', s.value)}
                />
                <span>{s.label}</span>
              </label>
            ))}
          </div>
        </fieldset>

        {error && <div className="error-banner">{error}</div>}
        {success && <div className="success-banner">{success}</div>}

        <button className="pref-save-btn" type="submit" disabled={saving}>
          {saving ? 'Saving…' : 'Save'}
        </button>
      </form>
    </div>
  );
}
