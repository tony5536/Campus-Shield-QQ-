# CampusShield AI

This repository contains the CampusShield AI project: a FastAPI backend, an admin React dashboard, ML services and edge components.

This README provides minimal, safe steps to run locally and deploy the Python backend to platforms like Render or Railway.

---

## Quick local run (backend)

1. Create a Python virtual environment and activate it:

```bash
python -m venv .venv
# Windows (PowerShell)
. .venv/Scripts/Activate.ps1
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies (top-level requirements delegates to `Backend/requirements.txt`):

```bash
pip install -r requirements.txt
```

3. Start the app (dev reload enabled):

```bash
# Option A: run with python entrypoint
python app.py

# Option B: run with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The health endpoint is at `http://localhost:8000/health`.

---

## Frontend (React dashboard)

1. Install and run the dashboard development server:

```bash
cd dashboard
npm install
npm start
```

2. Dashboard default dev URL: `http://localhost:3000`.

The React app reads API base URL from `dashboard/.env` (REACT_APP_API_URL).

---

## Deployment (Render or Railway)

Use one of these start commands in your service configuration:

- Render / Railway (command):

```
uvicorn app:app --host 0.0.0.0 --port $PORT
```

Or, for a production gunicorn setup (optional):

```
gunicorn -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:$PORT
```

Notes:
- Ensure you set environment variables on the hosting platform (`CS_SECRET_KEY`, `DATABASE_URL`, etc.).
- For production DB use PostgreSQL and update `DATABASE_URL`.

---

## What I changed and why

- Added top-level `app.py` so the application can be started with `python app.py` and `uvicorn app:app`.
- Added a root `requirements.txt` that delegates to `Backend/requirements.txt` (so `pip install -r requirements.txt` works from repo root).
- Added a root `.gitignore` to avoid committing local envs and build artifacts.
- Added README with clear local and platform deployment steps.

These are minimal, safe changes that do not change application logic.

---

If you want, I can also:
- Add a `Procfile` for Heroku-like platforms
- Create a small `Dockerfile` for containerized deployment
- Add a `render.yaml` or GitHub Actions workflow for CI/CD
# CampusShield AI
Project scaffold generated. Backend implemented with FastAPI in backend/app. Run with:
uvicorn backend.app.main:app --reload