import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { apiFetch } from '../../utils/api';
import './TailoredCVPage.css';

const SECTIONS = [
    { key: 'skills', label: 'Skills' },
    { key: 'experience', label: 'Experience' },
    { key: 'education', label: 'Education' },
];

function ChangeCard({ sectionKey, change, onStatusChange, saving }) {
    return (
        <article className="change-card">
            <div className="change-card-grid">
                <div className="change-column">
                    <span className="change-column-label">Before</span>
                    <p>{change.before}</p>
                </div>
                <div className="change-column">
                    <span className="change-column-label">After</span>
                    <p>{change.after}</p>
                </div>
            </div>

            <p className="change-reason">{change.reason}</p>

            <div className="change-actions">
                <button
                    type="button"
                    className={`change-action ${change.status === 'accepted' ? 'selected accepted' : ''}`}
                    disabled={saving}
                    onClick={() => onStatusChange(sectionKey, change.id, 'accepted')}
                >
                    Accept
                </button>
                <button
                    type="button"
                    className={`change-action ${change.status === 'rejected' ? 'selected rejected' : ''}`}
                    disabled={saving}
                    onClick={() => onStatusChange(sectionKey, change.id, 'rejected')}
                >
                    Reject
                </button>
            </div>
        </article>
    );
}

export default function TailoredCVPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [tailoredCVs, setTailoredCVs] = useState([]);
    const [selectedCV, setSelectedCV] = useState(null);
    const [loadingList, setLoadingList] = useState(true);
    const [loadingDetail, setLoadingDetail] = useState(false);
    const [savingChangeId, setSavingChangeId] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        async function fetchTailoredCVs() {
            try {
                const res = await apiFetch('/api/cv/tailored/');
                if (!res.ok) {
                    setError('Failed to load tailored CVs.');
                    return;
                }
                const data = await res.json();
                setTailoredCVs(data);
            } catch {
                setError('Could not connect to the server.');
            } finally {
                setLoadingList(false);
            }
        }

        fetchTailoredCVs();
    }, []);

    useEffect(() => {
        if (!id) {
            setSelectedCV(null);
            return;
        }

        async function fetchTailoredCVDetail() {
            setLoadingDetail(true);
            setError('');
            try {
                const res = await apiFetch(`/api/cv/tailored/${id}/`);
                if (!res.ok) {
                    setError('Failed to load tailored CV details.');
                    return;
                }
                const data = await res.json();
                setSelectedCV(data);
                setTailoredCVs((prev) => prev.map((item) => (item.id === data.id ? data : item)));
            } catch {
                setError('Could not connect to the server.');
            } finally {
                setLoadingDetail(false);
            }
        }

        fetchTailoredCVDetail();
    }, [id]);

    const selectedSummary = useMemo(
        () => selectedCV?.review_summary || { pending: 0, accepted: 0, rejected: 0, total: 0 },
        [selectedCV]
    );

    async function handleStatusChange(section, changeId, status) {
        if (!selectedCV) {
            return;
        }

        setSavingChangeId(changeId);
        setError('');

        try {
            const res = await apiFetch(`/api/cv/tailored/${selectedCV.id}/`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    changes: [{ section, id: changeId, status }],
                }),
            });

            if (!res.ok) {
                const data = await res.json();
                setError(data.error || 'Could not update this change.');
                return;
            }

            const updated = await res.json();
            setSelectedCV(updated);
            setTailoredCVs((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
        } catch {
            setError('Could not connect to the server.');
        } finally {
            setSavingChangeId('');
        }
    }

    if (loadingList) {
        return (
            <div className="tailored-page">
                <h1>Tailored CVs</h1>
                <div className="loading-state">
                    <div className="spinner" />
                    <p>Loading your tailored CVs…</p>
                </div>
            </div>
        );
    }

    return (
        <div className="tailored-page">
            <div className="page-header">
                <div>
                    <h1>Tailored CVs</h1>
                    <p className="tailored-subtitle">
                        Review each change before using a tailored CV for an application.
                    </p>
                </div>
                {id && (
                    <button type="button" className="back-link-btn" onClick={() => navigate('/tailored-cvs')}>
                        Back to all tailored CVs
                    </button>
                )}
            </div>

            {error && <div className="error-banner">{error}</div>}

            {!error && tailoredCVs.length === 0 && (
                <div className="empty-state">
                    <p>No tailored CVs yet. Go to <Link to="/jobs">Find Jobs</Link> and click "Tailor CV" on a listing.</p>
                </div>
            )}

            {tailoredCVs.length > 0 && (
                <div className="tailored-layout">
                    <aside className="tailored-list">
                        {tailoredCVs.map((tcv) => {
                            const isSelected = Number(id) === tcv.id;
                            const summary = tcv.review_summary || {};

                            return (
                                <button
                                    key={tcv.id}
                                    type="button"
                                    className={`tailored-card ${isSelected ? 'selected' : ''}`}
                                    onClick={() => navigate(`/tailored-cvs/${tcv.id}`)}
                                >
                                    <div className="tailored-card-title">
                                        <h3>{tcv.job_title}</h3>
                                        {tcv.job_company && <span className="tailored-company">{tcv.job_company}</span>}
                                    </div>
                                    <div className="tailored-card-meta">
                                        <span className="tailored-date">
                                            {new Date(tcv.created_at).toLocaleDateString()}
                                        </span>
                                        <span className="tailored-count">
                                            {summary.pending || 0} pending
                                        </span>
                                    </div>
                                </button>
                            );
                        })}
                    </aside>

                    <section className="tailored-detail">
                        {!id && (
                            <div className="empty-review-state">
                                <h2>Select a tailored CV</h2>
                                <p>Choose a job-specific version on the left to compare the original and tailored sections.</p>
                            </div>
                        )}

                        {id && loadingDetail && (
                            <div className="loading-state detail-loading">
                                <div className="spinner" />
                                <p>Loading review details…</p>
                            </div>
                        )}

                        {id && selectedCV && !loadingDetail && (
                            <>
                                <div className="detail-header">
                                    <div>
                                        <h2>{selectedCV.job_title}</h2>
                                        {selectedCV.job_company && <p className="detail-company">{selectedCV.job_company}</p>}
                                    </div>
                                    <div className="summary-badges">
                                        <span className="summary-badge pending">{selectedSummary.pending} pending</span>
                                        <span className="summary-badge accepted">{selectedSummary.accepted} accepted</span>
                                        <span className="summary-badge rejected">{selectedSummary.rejected} rejected</span>
                                    </div>
                                </div>

                                {SECTIONS.map((section) => {
                                    const changes = selectedCV.change_set?.[section.key] || [];

                                    return (
                                        <div key={section.key} className="review-section">
                                            <div className="review-section-header">
                                                <h3>{section.label}</h3>
                                                <span>{changes.length} changes</span>
                                            </div>

                                            {changes.length === 0 ? (
                                                <div className="section-empty">No tailored changes for this section.</div>
                                            ) : (
                                                <div className="change-list">
                                                    {changes.map((change) => (
                                                        <ChangeCard
                                                            key={change.id}
                                                            sectionKey={section.key}
                                                            change={change}
                                                            saving={savingChangeId === change.id}
                                                            onStatusChange={handleStatusChange}
                                                        />
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </>
                        )}
                    </section>
                </div>
            )}
        </div>
    );
}
