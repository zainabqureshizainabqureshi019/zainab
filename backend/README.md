# Smart Inventory API starter

This is a minimal FastAPI backend foundation. It provides API health checks and a PostgreSQL connectivity check. It does **not yet contain the product, supplier, purchase, inventory, customer, sales, or reporting endpoints**; those must be implemented against the exact schema and business rules from the existing Streamlit application.

## Local setup (run from the project root)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
Copy-Item backend/.env.example backend/.env
```

Edit `backend/.env` with the rotated Neon connection string and set `CORS_ORIGINS=http://localhost:5173`. Do not share or commit this file.

Load the variables before starting the API. From the project root:

```powershell
python -c "from dotenv import load_dotenv; load_dotenv('backend/.env')"
```

For a persistent shell session, use:

```powershell
$env:DATABASE_URL = "YOUR_ROTATED_NEON_CONNECTION_STRING"
$env:CORS_ORIGINS = "http://localhost:5173"
uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000/health`, `http://127.0.0.1:8000/health/database`, and `http://127.0.0.1:8000/docs`.

## Render settings (later)

- Root Directory: project root (where the `backend` folder lives)
- Build Command: `pip install -r backend/requirements.txt`
- Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Environment Variables: `DATABASE_URL` and `CORS_ORIGINS` (set the deployed Vercel origin)

Do not deploy until the business endpoints, authentication, schema compatibility, and automated tests have been completed.
