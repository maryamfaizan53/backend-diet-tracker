# md
# health-ai-backend

## Requirements
- Python 3.10+
- Docker (optional)
- Supabase project with POSTGRES and Row Level Security disabled for service_role operations

## Setup (local)
1. cp env.example .env  # set secrets
2. python -m venv .venv && source .venv/bin/activate
3. pip install -r requirements.txt
4. Apply DB migrations:
   psql "postgresql://<db_user>:<db_pass>@<db_host>:5432/<db_name>" -f migrations/01_create_tables.sql
   # Or use Supabase SQL editor and run the SQL file content.

5. Run:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000

## Docker
Build: docker build -t health-ai-backend:latest .
Run: docker run -e SUPABASE_URL=... -e SUPABASE_SERVICE_KEY=... -p 8000:8000 health-ai-backend:latest

## CI
Copy `github_actions_ci.yml` to `.github/workflows/ci.yml` (required by GitHub Actions).

## Security Notes
- Keep SUPABASE_SERVICE_KEY server-side only.
- Verify JWTs server-side using SUPABASE_JWT_SECRET.
- Rate limiting implemented in-memory; use Redis for production.

## API Examples
Generate insights:
