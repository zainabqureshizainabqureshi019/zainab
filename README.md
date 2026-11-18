# Smart Inventory & Sales Management System

A web-based inventory and sales management application for a local supermarket. The project uses Streamlit for the user interface, Python for application logic, Neon PostgreSQL for persistent data, and FastAPI for a separately deployed backend API.

## Live application

- **Streamlit application:** https://smart-inventory-zainab.streamlit.app/
- **FastAPI Swagger documentation:** https://zainab-two.vercel.app/docs
- **GitHub repository:** https://github.com/zainabqureshizainabqureshi019/zainab

## Technology stack

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Application logic | Python |
| Backend API | FastAPI |
| Database | Neon PostgreSQL |
| Data handling | Pandas |
| Charts | Plotly |
| API hosting | Vercel |
| Frontend hosting | Streamlit Community Cloud |

## Features

- Business dashboard with active products, stock totals, low-stock alerts, and sales overview
- Product catalogue with SKU, category, pricing, supplier, and stock information
- Inventory monitoring and replenishment visibility
- Sales entry and multi-product checkout
- Purchase entry with supplier and cost tracking
- Category, customer, and supplier management
- Staff accounts and role-based page access
- Sales and stock reports with CSV exports
- Print-ready sales bills

## Project structure

```text
.
├── app.py                 # Streamlit application entry point
├── db.py                  # PostgreSQL database helpers
├── styles.py              # UI styling
├── views/                 # Streamlit application pages
├── backend/               # FastAPI backend
├── schema.sql             # PostgreSQL database schema
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Backend project and Vercel configuration
├── Dockerfile
└── .env.example           # Example environment configuration
```

## Architecture and deployment

- The **Streamlit frontend** is deployed on Streamlit Community Cloud.
- The **FastAPI backend** is deployed on Vercel.
- **Neon PostgreSQL** stores the application's data.
- The current Streamlit database helper (`db.py`) connects directly to Neon using `DATABASE_URL`. The separately deployed FastAPI API is available through its Swagger documentation; frontend-to-API integration is not currently documented as complete.

## Run locally

### 1. Requirements

- Python compatible with the packages in `requirements.txt`
- A Neon PostgreSQL database
- Git and VS Code (recommended)

### 2. Create and activate a virtual environment

Windows PowerShell, from the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Set up the database

1. Open your Neon project and select **SQL Editor**.
2. Open `schema.sql` in this repository.
3. Run the schema in Neon if it has not already been applied. Do not repeatedly drop or recreate existing tables.
4. Copy your Neon PostgreSQL connection string from **Connection Details** and ensure SSL is enabled.

### 4. Configure the database connection

Create a local `.env` file beside `app.py` using `.env.example` as a guide, then set:

```env
DATABASE_URL=your-neon-connection-string
```

Alternatively, create `.streamlit/secrets.toml`:

```toml
DATABASE_URL = "your-neon-connection-string"
```

Never commit `.env` or `secrets.toml` to GitHub. Never publish database passwords, JWT secrets, access tokens, or screenshots containing secret values.

### 5. Start the Streamlit app

```powershell
streamlit run app.py
```

The local app is usually available at http://localhost:8501.

## Deployment configuration

### Streamlit Community Cloud

1. Connect the GitHub repository to Streamlit Community Cloud.
2. Select branch `main` and main file `app.py`.
3. Add `DATABASE_URL` in the app's **Settings → Secrets** using valid TOML syntax:

   ```toml
   DATABASE_URL = "your-neon-connection-string"
   ```

4. Save the secret and check the deployed app.

### Vercel (FastAPI backend)

1. Import the GitHub repository into Vercel.
2. Use the FastAPI project configuration in `pyproject.toml`.
3. Configure the required environment variables in Vercel Project Settings. Keep their values private.
4. Deploy from the `main` branch and verify the API through the Swagger URL above.

## Recommended first-use workflow

1. Sign in with an authorized account and change any temporary/default password immediately.
2. Add suppliers and categories.
3. Add customers when needed; walk-in sales are supported.
4. Add products and opening stock.
5. Record purchases when new stock arrives.
6. Record sales and review stock updates.
7. Review the Dashboard and Reports & Analytics.

## Security and operational notes

- Keep database connection strings and JWT signing secrets in hosting-provider secrets/environment settings, never in source code.
- If a temporary or default account password has been used, change it before sharing the live app.
- Back up the database regularly and restrict access to authorized users.
- Before real commercial use, review audit logging, role permissions, tax and receipt requirements, data backups, and operational security.
