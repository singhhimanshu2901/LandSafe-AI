# LandSafe-AI Production Deployment Guide

## 1. Prerequisites
- Node.js (v18+)
- Python (v3.11+)
- A Supabase project (PostgreSQL + Storage)
- A standard VPS (e.g., AWS EC2, DigitalOcean Droplet, Render, or Railway)

## 2. Supabase Configuration
Ensure your Supabase project is active and has:
- A `postgres` database instance.
- A private Storage bucket named `incident-evidence`.
- Retrieve your `Project URL` and `service_role` key from the Supabase dashboard (Project Settings > API).

## 3. Environment Variables
### Backend (`backend/.env`)
Create this file and do **NOT** commit it to version control:
```env
# Database
DATABASE_URL="postgresql://username:password@host:5432/dbname"

# FastAPI configuration
ENV="production"
SECRET_KEY="<generate_a_secure_random_string_here>"
ALLOWED_ORIGINS="https://your-frontend-domain.com"

# Supabase Storage Configuration
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_SERVICE_ROLE_KEY="<your-service-role-key>"
MAX_UPLOAD_SIZE_MB=10
```

### Frontend (`frontend/.env.production`)
Create this file for public configuration only:
```env
VITE_API_BASE="https://api.your-domain.com/api/v1"
```

## 4. Backend Deployment
We recommend running FastAPI via `gunicorn` with `uvicorn` workers.
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
*Note: A simple deployment on Render or Railway natively supports this via the `start` command.*

## 5. Frontend Deployment
The frontend is a static React Single Page Application (SPA).
```bash
cd frontend
npm install
npm run build
```
Serve the `dist/` folder via Nginx, Vercel, Netlify, or Cloudflare Pages.

## 6. Scheduler Deployment
The ML/Weather ingestion scheduler (`ml/scheduler_job.py`) **MUST NOT** be embedded within the FastAPI workers. If multiple API workers boot, they will create duplicate schedules and throttle the database.

**Production Scheduled Execution Uses GitHub Actions (Free & Recommended):**
A GitHub Actions workflow is provided (`.github/workflows/automatic-alerts.yml`) which runs the continuous pipeline cleanly in a free runner. 

**Workflow:** `.github/workflows/automatic-alerts.yml`
**Schedule:** Hourly (Note: GitHub Actions scheduling is approximate and may be delayed based on runner availability).
**Manual Execution:** Supported via `workflow_dispatch` through the GitHub UI.

To activate this, you **must** configure the following Repository Secrets in GitHub:
- `DATABASE_URL`
- `SECRET_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

**Alternative Background Worker Approach:**
If you prefer to run it continuously (e.g. on a paid cloud instance rather than GitHub Actions), deploy it as a dedicated Background Worker service.
- **Option A (Systemd):** Create a dedicated `.service` file executing `python ml/scheduler_job.py`.
- **Option B (Docker):** Run a standalone container executing only the scheduler script.
- **Option C (Cloud Platforms):** Deploy it as a dedicated "Background Worker" service.

## 7. Storage Configuration
The system uses backend-mediated uploads to Supabase Storage.
- Ensure `SUPABASE_SERVICE_ROLE_KEY` is present in the Backend `.env` only.
- The `incident-evidence` bucket must remain Private to prevent unauthenticated access. 
- If credentials are omitted, the backend gracefully handles uploads by rejecting them via a `503 Service Unavailable` response.

## 8. HTTPS Requirements
- **Frontend:** Must be served over HTTPS (Vercel/Netlify handle this automatically). PWA features require HTTPS.
- **Backend:** Must sit behind an SSL-terminating reverse proxy (e.g., Nginx with Certbot, or a managed cloud load balancer). 
- **Security Check:** There are no `verify=False` parameters left in the codebase; strict SSL verification is enforced on all outgoing requests.

## 9. CORS Configuration
FastAPI relies on the `ALLOWED_ORIGINS` environment variable to secure the API.
Ensure your backend `.env` restricts access to your explicit frontend domain:
`ALLOWED_ORIGINS="https://your-frontend.com"`

## 10. Health Check
Once deployed, verify backend health via:
`GET https://api.your-domain.com/api/v1/health`
Expected output: `{"status": "ok", "database": "connected", "ml_model": "available"}`

## 11. Troubleshooting
- **CORS Errors:** Verify the `ALLOWED_ORIGINS` exactly matches your frontend domain (no trailing slashes).
- **503 Storage Errors:** Your `SUPABASE_SERVICE_ROLE_KEY` is missing or invalid.
- **Stale/Missing Risk Data:** Ensure your isolated Scheduler process is actively running and has its own `DATABASE_URL` configured in the environment.

## 12. Rollback Procedure
If a deployment fails:
1. Revert to the previous git commit.
2. Restart the API workers (`systemctl restart api` or cloud interface).
3. Database migrations (if any were applied via `alembic`) must be explicitly downgraded if breaking schemas were introduced.
