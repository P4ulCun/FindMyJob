import { useState, useEffect } from 'react';
import { apiFetch, authHeaders } from '../../utils/api';
import './CoverLettersPage.css';

export default function CoverLettersPage() {
    const [letters, setLetters] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [expandedId, setExpandedId] = useState(null);
    const [editingId, setEditingId] = useState(null);
    const [editBody, setEditBody] = useState('');
    const [saving, setSaving] = useState(false);
    const [saveMsg, setSaveMsg] = useState('');

    useEffect(() => {
        async function fetchLetters() {
            try {
                const res = await apiFetch('/api/cv/cover-letters/');
                if (!res.ok) {
                    setError('Failed to load cover letters.');
                    return;
                }
                const data = await res.json();
                setLetters(data);
            } catch {
                setError('Could not connect to the server.');
            } finally {
                setLoading(false);
            }
        }
        fetchLetters();
    }, []);

    function toggleExpand(id) {
        setExpandedId((prev) => (prev === id ? null : id));
        setEditingId(null);
        setSaveMsg('');
    }

    function startEditing(letter) {
        setEditingId(letter.id);
        setEditBody(letter.body);
        setSaveMsg('');
    }

    function cancelEditing() {
        setEditingId(null);
        setEditBody('');
        setSaveMsg('');
    }

    async function handleSave(id) {
        setSaving(true);
        setSaveMsg('');
        try {
            const res = await apiFetch(`/api/cv/cover-letters/${id}/`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ body: editBody }),
            });
            if (res.ok) {
                const updated = await res.json();
                setLetters((prev) =>
                    prev.map((l) => (l.id === id ? { ...l, body: updated.body } : l))
                );
                setEditingId(null);
                setSaveMsg('Saved!');
            } else {
                setSaveMsg('Save failed.');
            }
        } catch {
            setSaveMsg('Network error.');
        } finally {
            setSaving(false);
        }
    }

    async function handleDownload(id, jobTitle) {
        try {
            const res = await fetch(`/api/cv/cover-letters/${id}/download/`, {
                headers: authHeaders(),
            });
            if (!res.ok) return;
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            const safeTitle = jobTitle.replace(/[^a-zA-Z0-9 _-]/g, '').slice(0, 50);
            a.href = url;
            a.download = `Cover_Letter_${safeTitle}.docx`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch {
            // silently fail
        }
    }

    if (loading) {
        return (
            <div className="cl-page">
                <h1>Cover Letters</h1>
                <div className="loading-state">
                    <div className="spinner" />
                    <p>Loading your cover letters…</p>
                </div>
            </div>
        );
    }

    return (
        <div className="cl-page">
            <h1>Cover Letters</h1>
            <p className="cl-subtitle">
                AI-generated cover letters personalized for each job listing.
            </p>

            {error && <div className="error-banner">{error}</div>}

            {!error && letters.length === 0 && (
                <div className="empty-state">
                    <p>No cover letters yet. Go to <a href="/jobs">Find Jobs</a> and click "📝 Cover Letter" on a listing.</p>
                </div>
            )}

            <div className="cl-list">
                {letters.map((letter) => {
                    const isExpanded = expandedId === letter.id;
                    const isEditing = editingId === letter.id;
                    return (
                        <div key={letter.id} className={`cl-card ${isExpanded ? 'expanded' : ''}`}>
                            <button className="cl-card-header" onClick={() => toggleExpand(letter.id)}>
                                <div className="cl-card-title">
                                    <h3>{letter.job_title}</h3>
                                    {letter.job_company && <span className="cl-company">{letter.job_company}</span>}
                                </div>
                                <div className="cl-card-meta">
                                    <span className="cl-date">
                                        {new Date(letter.created_at).toLocaleDateString()}
                                    </span>
                                    <span className={`expand-icon ${isExpanded ? 'open' : ''}`}>▾</span>
                                </div>
                            </button>

                            {isExpanded && (
                                <div className="cl-card-body">
                                    {isEditing ? (
                                        <>
                                            <textarea
                                                className="cl-edit-textarea"
                                                value={editBody}
                                                onChange={(e) => setEditBody(e.target.value)}
                                                rows={14}
                                            />
                                            <div className="cl-edit-actions">
                                                <button className="cl-save-btn" onClick={() => handleSave(letter.id)} disabled={saving}>
                                                    {saving ? 'Saving…' : 'Save'}
                                                </button>
                                                <button className="cl-cancel-btn" onClick={cancelEditing}>Cancel</button>
                                            </div>
                                        </>
                                    ) : (
                                        <>
                                            <div className="cl-body-text">
                                                {letter.body.split('\n').map((line, i) => (
                                                    <p key={i}>{line || '\u00A0'}</p>
                                                ))}
                                            </div>
                                            <div className="cl-actions">
                                                <button className="cl-edit-btn" onClick={() => startEditing(letter)}>
                                                    ✏️ Edit
                                                </button>
                                                <button
                                                    className="cl-download-btn"
                                                    onClick={() => handleDownload(letter.id, letter.job_title)}
                                                >
                                                    📥 Download .docx
                                                </button>
                                            </div>
                                        </>
                                    )}
                                    {saveMsg && <div className="cl-save-msg">{saveMsg}</div>}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
