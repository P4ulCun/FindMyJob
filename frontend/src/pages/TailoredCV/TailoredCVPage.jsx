import { useState, useEffect } from 'react';
import { apiFetch } from '../../utils/api';
import './TailoredCVPage.css';

export default function TailoredCVPage() {
    const [tailoredCVs, setTailoredCVs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [expandedId, setExpandedId] = useState(null);

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
                setLoading(false);
            }
        }
        fetchTailoredCVs();
    }, []);

    function toggleExpand(id) {
        setExpandedId((prev) => (prev === id ? null : id));
    }

    if (loading) {
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
            <h1>Tailored CVs</h1>
            <p className="tailored-subtitle">
                CV versions tailored by AI for specific job listings.
            </p>

            {error && <div className="error-banner">{error}</div>}

            {!error && tailoredCVs.length === 0 && (
                <div className="empty-state">
                    <p>No tailored CVs yet. Go to <a href="/jobs">Find Jobs</a> and click "Tailor CV" on a listing.</p>
                </div>
            )}

            <div className="tailored-list">
                {tailoredCVs.map((tcv) => {
                    const isExpanded = expandedId === tcv.id;
                    return (
                        <div key={tcv.id} className={`tailored-card ${isExpanded ? 'expanded' : ''}`}>
                            <button className="tailored-card-header" onClick={() => toggleExpand(tcv.id)}>
                                <div className="tailored-card-title">
                                    <h3>{tcv.job_title}</h3>
                                    {tcv.job_company && <span className="tailored-company">{tcv.job_company}</span>}
                                </div>
                                <div className="tailored-card-meta">
                                    <span className="tailored-date">
                                        {new Date(tcv.created_at).toLocaleDateString()}
                                    </span>
                                    <span className={`expand-icon ${isExpanded ? 'open' : ''}`}>▾</span>
                                </div>
                            </button>

                            {isExpanded && (
                                <div className="tailored-card-body">
                                    <div className="tailored-section">
                                        <h4>Tailored Skills</h4>
                                        <ul>
                                            {(tcv.tailored_skills || []).map((skill, i) => (
                                                <li key={i}>{skill}</li>
                                            ))}
                                        </ul>
                                    </div>

                                    <div className="tailored-section">
                                        <h4>Tailored Experience</h4>
                                        <ul>
                                            {(tcv.tailored_experience || []).map((exp, i) => (
                                                <li key={i}>{exp}</li>
                                            ))}
                                        </ul>
                                    </div>

                                    <div className="tailored-section">
                                        <h4>Tailored Education</h4>
                                        <ul>
                                            {(tcv.tailored_education || []).map((edu, i) => (
                                                <li key={i}>{edu}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
