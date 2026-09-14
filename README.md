# Argo Controls Platform

A Flask REST API for sharing Python utilities with a React frontend (in progress, in `frontend/`). The Flask backend exposes all features as JSON endpoints under `/api/`; the legacy Jinja2 views remain during the frontend transition.

## Project Structure

```
├── acp_app/
│   ├── api/                  REST API blueprints (JSON responses for React)
│   ├── services/             Business logic — no HTTP awareness
│   ├── views/                Legacy Jinja2 views (routes only, to be removed post-React)
│   ├── static/               CSS and images (legacy)
│   ├── templates/            Jinja2 HTML templates (legacy)
│   ├── data/
│   │   └── raw/              Source CSVs and XLS files for seeding the database
│   ├── commands.py           Flask CLI commands (init-db, init-team, etc.)
│   ├── models.py             SQLAlchemy ORM models
│   └── __init__.py           App factory
├── frontend/                 React + Vite + Tailwind app (see frontend/README.md)
├── instance/                 SQLite database lives here (gitignored)
├── tests/
├── .env.example              Template for environment variables
├── app.py                    Entry point
├── config.py                 Flask configuration classes
├── dev.sh                    Developer workflow script
├── requirements.txt
└── web.config                wfastcgi config for IIS
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/team` | Team members list |
| GET | `/api/aspen/search/<term>` | Aspen IO + IP tag search |
| GET | `/api/aspen/status` | Aspen IO status |
| GET | `/api/intellution/<term>?col=tag` | Intellution tag search |
| POST | `/api/gcc/eos` | EOS code → plain English |
| GET | `/api/ttparser/<name>/<seq>` | Truthtable lookup |

## First-Time Setup

1. Create and fill in your local environment file:
   ```bash
   cp .env.example .env.local
   # edit .env.local with your values
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   ./dev.sh flask init-db
   ```

4. Seed the database with your data files:
   ```bash
   ./dev.sh flask init-intellution  # requires files in acp_app/data/raw/intellution/
   ./dev.sh flask init-team         # requires files in acp_app/data/raw/team/
   ./dev.sh flask init-ttparser     # requires files in acp_app/data/raw/gcc/
   ```

5. Start the Flask dev server on port 5001 (the React dev server proxies `/api` there):
   ```bash
   ./dev.sh flask run --debug --port 5001
   ```

6. In a second terminal, install frontend dependencies and start the React dev server:
   ```bash
   cd frontend
   npm install      # first time only
   npm run dev
   ```
   Open http://localhost:5173.

## Running the Frontend

The React app lives in `frontend/` and requires Node.js. During development, run **both** servers:

| Terminal | Command | URL |
|----------|---------|-----|
| 1 (project root) | `./dev.sh flask run --debug --port 5001` | http://localhost:5001 |
| 2 (`frontend/`) | `npm run dev` | http://localhost:5173 |

Vite forwards any request starting with `/api` to `http://localhost:5001` (configured in `frontend/vite.config.js`), so frontend code calls relative paths like `fetch('/api/team')`. If Flask runs on a different port, API calls from the frontend will fail.

See [frontend/README.md](frontend/README.md) for the other npm scripts.

## CLI Commands

All commands are run via `dev.sh` to ensure the environment is loaded:

| Command | Description |
|---------|-------------|
| `./dev.sh flask init-db` | Create all database tables |
| `./dev.sh flask init-intellution` | Load Intellution tag data |
| `./dev.sh flask init-team` | Load team and unit data |
| `./dev.sh flask init-ttparser` | Load GCC Truthtable data |
| `./dev.sh flask run --debug --port 5001` | Start Flask dev server |

## Data File Schemas

### `acp_app/data/raw/team/team.csv`

One row per person. Multiple units for one person are separated by `|`.

| Column | Type | Description |
|--------|------|-------------|
| `name` | string | Full name |
| `role` | string | Job title |
| `email` | string | Email address (can be blank) |
| `linkedin` | string | Full LinkedIn URL (can be blank) |
| `active` | boolean | `true` to show, `false` to hide |
| `units` | string | Plant areas, pipe-separated: `Unit1\|Unit2` |

Example:
```csv
name,role,email,linkedin,active,units
John Doe,Controls Engineer,John@company.com,,true,Unit1|Unit2
Jane Doesnt,Controls Engineer,,,true,Utilities
```

## Environment Variables

See `.env.example` for a full template. Key variables:

| Variable | Description |
|----------|-------------|
| `FLASK_APP` | Entry point (`app.py`) |
| `FLASK_CONFIG` | `development`, `testing`, or `production` |
| `SECRET_KEY` | Random secret string |
| `DEV_DATABASE_URL` | Dev DB — `sqlite:///data.sqlite` for local SQLite |
| `DATABASE_URL` | Production DB URL |
| `ASPEN_SERVER` | Aspen server hostname |
| `CORS_ORIGINS` | Allowed origins for the API, comma-separated (default: `http://localhost:5173`) |