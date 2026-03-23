# Project: Job Hunt Duo
## System Context & Architecture

### 1. Tech Stack
* **Frontend:** React + Vite
* **Backend:** Django (Python 3.11+) + Django REST Framework
* **Database:** PostgreSQL
* **Infrastructure:** Docker Compose (local development with volume mounts for hot-reloading)

### 2. Core Agent Instructions
* Always provide clean, production-ready code.
* Ensure CORS is configured properly between React (port 5173) and Django (port 8000).
* Do not use deprecated libraries (e.g., use Vite, not Create React App).
* Keep Dockerfiles minimal and focused on development.

---

## Product Backlog & Features

### EPIC 1: User Management
* **US-01/02:** Job seekers can register/login with email and password. Needs session persistence and password reset capabilities.

### EPIC 2: CV Upload & Parsing
* **US-03/04:** Users can upload a PDF CV (up to 5MB). The system automatically extracts name, skills, experience, and education. Users can inline-edit this parsed data before saving.

### EPIC 3: Job Preferences
* **US-05/06:** Users set preferences (title, location, remote/hybrid, seniority). Users select which external APIs to query (Adzuna, RemoteOK, etc.).

### EPIC 4: Agent 1 — Job Finder Bot
* **US-07/08/09:** Runs on a schedule, queries APIs, removes duplicates. 
* Uses semantic similarity to compare the user's CV to the job description, assigning a 0-100% Match Score.
* Generates a 2-3 sentence AI summary of the listing.

### EPIC 5: Agent 2 — CV Tailor Bot
* **US-10/11/12:** Triggered manually per job. Rewrites CV bullet points to match job keywords (without fabricating skills). 
* Generates a personalized cover letter (.docx/PDF export). 
* Shows a side-by-side diff view explaining why changes were made.

### EPIC 6: Digest & Tracking
* **US-13/14/15:** Sends periodic email digests with top matches.
* Provides a Kanban-style tracking system (Saved, Applied, Rejected). 
* The entire React frontend must be mobile-responsive.