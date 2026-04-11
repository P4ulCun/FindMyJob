import { useState, useRef } from 'react';
import { authHeaders } from '../../utils/api';
import './CVPage.css';

const MAX_SIZE = 5 * 1024 * 1024; // 5 MB
const API_UPLOAD = '/api/cv/upload/';
const API_CV = '/api/cv/'; // + :id/

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export default function CVPage() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [cvId, setCvId] = useState(null);
  const [preview, setPreview] = useState(null);
  const [editData, setEditData] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef();

  // ---- validation ----
  const validate = (f) => {
    if (!f) return 'Please select a file.';
    if (!f.name.toLowerCase().endsWith('.pdf')) return 'Only .pdf files are accepted.';
    if (f.size > MAX_SIZE) return `File exceeds 5 MB (${formatBytes(f.size)}).`;
    return '';
  };

  const handleFileChange = (f) => {
    setSuccess('');
    const err = validate(f);
    setError(err);
    setFile(err ? null : f);
  };

  const onInputChange = (e) => handleFileChange(e.target.files[0]);

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFileChange(e.dataTransfer.files[0]);
    if (inputRef.current) inputRef.current.value = '';
  };

  // ---- upload ----
  const handleUpload = async () => {
    if (!file) return;
    setError('');
    setSuccess('');
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(API_UPLOAD, {
        method: 'POST',
        headers: authHeaders(),
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || data.detail || 'Upload failed.');
        return;
      }
      setCvId(data.id);
      setPreview(data);
      setEditData({
        extracted_name: data.extracted_name || '',
        extracted_skills: data.extracted_skills || [],
        extracted_experience: data.extracted_experience || [],
        extracted_education: data.extracted_education || [],
      });
      setFile(null);
      if (inputRef.current) inputRef.current.value = '';
    } catch {
      setError('Network error — could not reach the server.');
    } finally {
      setLoading(false);
    }
  };

  // ---- save edits (PATCH) ----
  const handleSave = async () => {
    if (!cvId || !editData) return;
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      const res = await fetch(`${API_CV}${cvId}/`, {
        method: 'PATCH',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(editData),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || data.detail || 'Save failed.');
        return;
      }
      setPreview(data);
      setSuccess('Changes saved successfully.');
    } catch {
      setError('Network error — could not reach the server.');
    } finally {
      setSaving(false);
    }
  };

  // ---- re-upload ----
  const handleReupload = () => {
    setCvId(null);
    setPreview(null);
    setEditData(null);
    setFile(null);
    setError('');
    setSuccess('');
    if (inputRef.current) inputRef.current.value = '';
  };

  // ---- helpers for editable list fields ----
  const listToText = (arr) => (Array.isArray(arr) ? arr.join('\n') : arr);
  const textToList = (text) => text.split('\n').filter((l) => l.trim() !== '');

  const updateField = (field, value) => {
    setEditData((prev) => ({ ...prev, [field]: value }));
    setSuccess('');
  };

  // ---- render ----
  // Upload form (shown when no CV has been uploaded yet)
  const uploadForm = (
    <>
      <div
        className={`upload-card${dragOver ? ' drag-over' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <label className="file-input-label">
          Choose PDF
          <input ref={inputRef} type="file" accept=".pdf" onChange={onInputChange} />
        </label>
        <p>or drag &amp; drop a .pdf file here (max 5 MB)</p>

        {file && (
          <div className="selected-file">
            <span className="file-name">{file.name}</span>
            <span className="file-size">({formatBytes(file.size)})</span>
          </div>
        )}
      </div>

      <button className="upload-btn" disabled={!file || loading} onClick={handleUpload}>
        {loading ? 'Uploading…' : 'Upload & Parse'}
      </button>
    </>
  );

  // Editable preview (shown after successful upload)
  const editablePreview = editData && (
    <section className="preview-section">
      <h2>Structured Preview</h2>

      <div className="preview-block">
        <h3>Name</h3>
        <div className="editable-field">
          <span className="edit-hint">click to edit</span>
          <input
            className="editable-input"
            value={editData.extracted_name}
            onChange={(e) => updateField('extracted_name', e.target.value)}
          />
        </div>
      </div>

      <div className="preview-block">
        <h3>Skills</h3>
        <div className="editable-field">
          <span className="edit-hint">one per line · click to edit</span>
          <textarea
            className="editable-input"
            rows={Math.max(3, editData.extracted_skills.length + 1)}
            value={listToText(editData.extracted_skills)}
            onChange={(e) => updateField('extracted_skills', textToList(e.target.value))}
            onInput={(e) => updateField('extracted_skills', e.target.value.split('\n'))}
          />
        </div>
      </div>

      <div className="preview-block">
        <h3>Experience</h3>
        <div className="editable-field">
          <span className="edit-hint">one per line · click to edit</span>
          <textarea
            className="editable-input"
            rows={Math.max(3, editData.extracted_experience.length + 1)}
            value={listToText(editData.extracted_experience)}
            onChange={(e) => updateField('extracted_experience', textToList(e.target.value))}
            onInput={(e) => updateField('extracted_experience', e.target.value.split('\n'))}
          />
        </div>
      </div>

      <div className="preview-block">
        <h3>Education</h3>
        <div className="editable-field">
          <span className="edit-hint">one per line · click to edit</span>
          <textarea
            className="editable-input"
            rows={Math.max(3, editData.extracted_education.length + 1)}
            value={listToText(editData.extracted_education)}
            onChange={(e) => updateField('extracted_education', textToList(e.target.value))}
            onInput={(e) => updateField('extracted_education', e.target.value.split('\n'))}
          />
        </div>
      </div>

      <div className="btn-row">
        <button className="save-btn" disabled={saving} onClick={handleSave}>
          {saving ? 'Saving…' : 'Save'}
        </button>
        <button className="reupload-btn" onClick={handleReupload}>
          Re-upload new CV
        </button>
      </div>
    </section>
  );

  return (
    <div className="cv-page">
      <h1>Upload your CV</h1>

      {!preview && uploadForm}

      {error && <div className="error-banner">{error}</div>}
      {success && <div className="success-banner">{success}</div>}

      {editablePreview}
    </div>
  );
}
