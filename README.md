# Smart Inventory

A modern inventory, purchasing, and sales workspace for supermarket teams, built
with Streamlit, Python, and Neon PostgreSQL.

## Features

- Business overview with daily sales, stock totals, and low-stock alerts
- Product catalogue, opening stock, categories, and suppliers
- Inventory monitoring and replenishment visibility
- Multi-product checkout that validates and updates stock
- Print-ready A4 bills for recent sales, with PDF saving through the browser
- Purchase entry with supplier and cost tracking
- Customer records and staff account management
- Sales and stock reports with CSV exports and a 30-day sales summary

## Requirements

- Python 3.10 or newer
- A Neon PostgreSQL database
- VS Code (recommended)

## Set up the Python environment

Windows PowerShell, from this project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `py` is not recognized, install Python from python.org and enable the PATH option, then reopen VS Code.

## Set up the database

1. Open your Neon project and select **SQL Editor**.
2. Open `schema.sql` from this folder, copy its complete contents into the Neon SQL Editor and run it once.
3. In Neon, open **Connection Details** and copy the PostgreSQL connection string. Use the pooled connection string if your Neon screen offers one; ensure SSL is enabled.

## Configure the database connection

Create a file named `.env` in the same folder as `app.py` by copying `.env.example`.

Put your own Neon connection string on the `DATABASE_URL=` line. Do not share `.env`, screenshots containing the password, or commit it to GitHub. The `.gitignore` already excludes `.env`.

Alternatively, create `.streamlit/secrets.toml` with:

```toml
DATABASE_URL = "your-neon-connection-string"
```

## Run locally

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

Streamlit will show a local URL, usually `http://localhost:8501`.

If you activated the virtual environment first, `streamlit run app.py` works too.

## Deploy on Railway

This project includes a Dockerfile that listens on Railway's assigned `PORT`.
Before deploying, rotate any database password that has been shared and use
only the new Neon connection string.

1. Install the Railway CLI using the [official installation guide](https://docs.railway.com/cli#installing-the-cli).
2. Open PowerShell in this project folder and sign in:

   ```powershell
   railway login
   ```

3. Create and select a Railway project, then upload the application:

   ```powershell
   railway init
   railway up
   ```

4. In the Railway project, open the app service's **Variables** and add
   `DATABASE_URL` with the new Neon connection string. Never upload `.env` or
   paste the connection string into source code.
5. In the service's **Settings → Networking**, generate a public domain. Open
   the generated URL to access the app from other devices.

Railway account plans, trial allowances, and usage-based charges can change.
Check the current pricing and limits before deploying.

## Initial administrator sign-in

- Username: `admin`
- Temporary password: `ChangeMe123!`

Change this password immediately from **Account & Users** after signing in. The initial admin is inserted by `schema.sql` only if the username does not already exist.

## Recommended setup order

1. Change the administrator password.
2. Add suppliers and categories.
3. Add customers (optional; walk-in sales are supported).
4. Add products and opening stock.
5. Record purchases when new stock arrives.
6. Record sales; the app checks stock and deducts sold quantities.
7. Review Dashboard and Reports & Analytics.

## Operational notes

- Run `schema.sql` once before starting the app. Do not repeatedly drop or recreate tables.
- Sales and purchase entries update their related stock within a single database transaction.
- This is a learning/development baseline. Before real commercial deployment, add backups, audit logs, stronger role permissions, tax/receipt rules, and deployment secrets management.
